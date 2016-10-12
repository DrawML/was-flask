import json
from datetime import datetime

import pickle

from io import BytesIO
from flask import Blueprint, request, current_app, render_template, g
from flask import flash
from flask import send_file
from flask_login import login_required
from jinja2.exceptions import TemplateError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import update

from app.common.object_code.util import ExperimentError, DataProcessor, TaskRunner, TFConverter
from app.dist_task.src.dist_system.client import Client
from app.dist_task.src.dist_system.master.virtualizer.config import RunConfig
from app.dist_task.src.dist_system.master.virtualizer.linker import link
from app.experiment.models import Refiner, JsonParser
from app.mysql import DrawMLRepository
from app.mysql_models import Experiment, Data
from app.redis import redis_cache, RedisKeyMaker
from app.response import ErrorResponse

module_exp = Blueprint('experiment',
                       __name__,
                       url_prefix='/experiments',
                       static_folder='/static/experiments',
                       template_folder='templates/experiments')
db = DrawMLRepository().db


@module_exp.route('/', methods=['GET'], endpoint='get_all_exp')
@login_required
def get_all_exp():
    return render_template('/experiment/list.html',
                           experiments=Experiment.query.
                           filter_by(user_id=g.user.id).order_by(Experiment.date_modified.desc()).all())
    """
    experiments = db.session.query(Experiment).filter(Experiment.user_id == user_id).all()
    refined_exps = Refiner(experiments)
    json.dumps(refined_exps.exps)
    current_app.logger.info('exp for ' + user_id + ' : ' + str(len(experiments)))
    return json.dumps(refined_exps.exps)
    """


@module_exp.route('/api/<exp_id>', methods=['GET'], endpoint='get_exp_api')
@login_required
def get_exp_api(exp_id):
    try:
        experiment = db.session.query(Experiment).filter(Experiment.id == exp_id).first()
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return ErrorResponse(500, 'Internal Database Error')
    if experiment is None:
        return ErrorResponse(400, 'Bad Request, No data')
    refined_exps = Refiner(experiment)
    current_app.logger.info('GET exp <%r>', refined_exps.exps['name'])
    return json.dumps(refined_exps.exps)


@module_exp.route('/<exp_id>', methods=['GET'], endpoint='get_exp_view')
@login_required
def get_exp_view(exp_id):
    try:
        experiment = db.session.query(Experiment).filter(Experiment.id == exp_id).first()
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return ErrorResponse(500, 'Internal Database Error')
    if experiment is None:
        return ErrorResponse(400, 'Bad Request, No data')
    return render_template('/experiment/draw.html',
                           exp_id=experiment.id)


@module_exp.route('/create', methods=['GET'], endpoint='create_view')
@login_required
def create_view():
    return render_template('/experiment/create.html')


@module_exp.route('/', methods=['POST'], endpoint='exp_create')
@login_required
def exp_create():
    json_data = request.get_json()
    exp_data = JsonParser.parse_post(json_data, g.user.id)
    if type(exp_data) != Experiment:
        current_app.logger.error(exp_data)
        return ErrorResponse(400, 'Json key Error')

    try:
        experiments = db.session.query(Experiment) \
            .filter(Experiment.user_id == exp_data.user_id,
                    Experiment.name == exp_data.name).all()
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return ErrorResponse(500, 'Error, Database Internal Error')
    if len(experiments) > 0:
        return ErrorResponse(400, 'Experiment name is Duplicated')

    try:
        db.session.add(exp_data)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return ErrorResponse(500, 'Error, Database Internal Error')
    current_app.logger.info('exp_data created :' + exp_data.name + ' ' + exp_data.user.user_id)
    return 'created'


@module_exp.route('/<exp_id>', methods=['PATCH'], endpoint='exp_update')
@login_required
def exp_update(exp_id):
    json = request.get_json()
    if json.get('exp_data', None) is None:
        ErrorResponse(400, 'No exp_data')

    drawing = json['exp_data'].get('drawing', None)
    xml = json['exp_data'].get('xml', None)
    if drawing is None or xml is None:
        ErrorResponse(400, 'Invalid Json form')

    try:
        exp_data = db.session.query(Experiment).filter(Experiment.id == exp_id).first()
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return ErrorResponse(500, 'Internal Database Error')
    if exp_data is None:
        return ErrorResponse(400, 'Bad Request, No data')

    exp_data.drawing = pickle.dumps(drawing)
    exp_data.xml = pickle.dumps(xml)
    exp_data.date_modified = datetime.now()
    try:
        update(Experiment).where(Experiment.id == exp_id).\
            values(date_modified=datetime.now(),
                   drawing=drawing,
                   xml=xml)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return ErrorResponse(500, 'Error, Database Internal Error')
    current_app.logger.info(' columns updated : ' + str(exp_data))
    return 'updated'


@module_exp.route('/<exp_id>', methods=['DELETE'], endpoint='exp_delete')
@login_required
def exp_delete(exp_id):
    try:
        deleted = db.session.query(Experiment) \
            .filter(Experiment.id == exp_id) \
            .delete(synchronize_session=False)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return ErrorResponse(500, 'Error, Database Internal Error')
    current_app.logger.info(str(deleted) + ' columns deleted : ' + exp_id)
    return 'delete'


@module_exp.route('/<exp_id>/run', methods=['POST'], endpoint='exp_run')
@login_required
def exp_run(exp_id):
    try:
        experiment = db.session.query(Experiment).filter(Experiment.id == exp_id).first()
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return ErrorResponse(500, 'Internal Database Error')
    if experiment is None:
        return ErrorResponse(400, 'Bad Request, No data')

    xml = request.data.decode()
    xml = ''.join(xml.split('\n'))

    data_key = RedisKeyMaker.make_key(id=exp_id,
                                      type=RedisKeyMaker.DATA_PROCESSING)
    model_key = RedisKeyMaker.make_key(id=exp_id,
                                       type=RedisKeyMaker.MODEL_TRAINING)
    data_cache = redis_cache.get(data_key)
    model_cache = redis_cache.get(model_key)
    if data_cache and data_cache.decode() == redis_cache.RUNNING:
        return ErrorResponse(400, 'Experiment is running now')
    if model_cache and model_cache.decode() == redis_cache.RUNNING:
        return ErrorResponse(400, 'Experiment is running now')

    print()
    print()
    print()
    print(xml)
    print()
    print()
    print()

    data_obj_code = None
    data_input_files = None
    try:
        data_processor = DataProcessor(xml)
        data_obj_code, file_ids = data_processor.generate_object_code()
        data_input_files = []
        for file_id in file_ids:
            fetched = Data.query.filter_by(id=int(file_id)).first()
            if not fetched:
                raise SQLAlchemyError('No data in database')
            data_input_files.append(fetched.path)
        current_app.logger.info('Code was generated')
        # data_processor.run_obj_code(data_obj_code)
    except ExperimentError:
        current_app.logger.error('Invalid XML form')
        return ErrorResponse(400, 'Invalid XML form')
    except TemplateError as e:
        current_app.logger.error(e)
        return ErrorResponse(500, 'Internal Server Error, Template Error')
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return ErrorResponse(500, 'Database Error')
    except AttributeError:
        current_app.logger.info('No data processing in XML')
    except Exception as e:
        current_app.logger.error(e)
        return ErrorResponse(500, 'Unexpected Error')

    model_obj_code = None
    if data_obj_code and data_input_files:
        model_input_file = True  # In this case, model file will be filled after data processing
    else:
        model_input_file = None
    try:
        tf_train_converter = TFConverter(xml, TFConverter.TYPE.TRAIN)
        model_obj_code, file_id = tf_train_converter.generate_object_code()
        if not model_input_file:
            fetched = Data.query.filter_by(id=int(file_id)).first()
            if not fetched:
                raise SQLAlchemyError('No data in database')
            model_input_file = fetched.path
        current_app.logger.info('Code was generated')
        # tf_converter.run_obj_code(model_obj_code)
    except ExperimentError:
        current_app.logger.error('Invalid XML form')
        return ErrorResponse(400, 'Invalid XML form')
    except TemplateError as e:
        current_app.logger.error(e)
        return ErrorResponse(500, 'Internal Server Error, Template Error')
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return ErrorResponse(500, 'Database Error')
    except AttributeError:
        current_app.logger.info('No model in XML')
    except Exception as e:
        current_app.logger.error(e)
        return ErrorResponse(500, 'Unexpected Error')

    valid = TaskRunner(user_id=g.user.id,
                       xml=xml,
                       data_obj_code=data_obj_code,
                       data_input_files=data_input_files,
                       data_key=data_key,
                       train_obj_code=model_obj_code,
                       train_input_file=model_input_file,
                       train_key=model_key).run()
    if valid is False:
        return 'Invalid request, Task is not done'
    return 'run'


@module_exp.route('/<exp_id>/stop', methods=['DELETE'], endpoint='exp_stop')
@login_required
def exp_stop(exp_id):
    try:
        experiment = db.session.query(Experiment).filter(Experiment.id == exp_id).first()
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        flash('Internal Database Error')
        return ErrorResponse(500, 'Internal Database Error')
    if experiment is None:
        flash('Bad Request, No data')
        return ErrorResponse(400, 'Bad Request, No data')

    data_key = RedisKeyMaker.make_key(id=exp_id,
                                      type=RedisKeyMaker.DATA_PROCESSING)
    model_key = RedisKeyMaker.make_key(id=exp_id,
                                       type=RedisKeyMaker.MODEL_TRAINING)
    data_value = redis_cache.get(data_key)
    if data_value is not None:
        if data_value.decode() == redis_cache.RUNNING:
            Client().request_cancel(data_key)
            flash('task was canceled')
            return 'task was canceled'

    model_value = redis_cache.get(model_key)
    if model_value is not None:
        if model_value.decode() == redis_cache.RUNNING:
            Client().request_cancel(model_key)
            flash('task was canceled')
            return 'task was canceled'

    return 'Nothing changed'


@module_exp.route('/<exp_id>/status', methods=['GET'], endpoint='exp_status')
@login_required
def exp_status(exp_id):
    try:
        experiment = db.session.query(Experiment).filter(Experiment.id == exp_id).first()
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return ErrorResponse(500, 'Internal Database Error')
    if experiment is None:
        return ErrorResponse(400, 'Bad Request, No data')

    data_key = RedisKeyMaker.make_key(id=exp_id,
                                      type=RedisKeyMaker.DATA_PROCESSING)
    model_key = RedisKeyMaker.make_key(id=exp_id,
                                       type=RedisKeyMaker.MODEL_TRAINING)
    model_value = redis_cache.get(model_key)
    data_value = redis_cache.get(data_key)

    if model_value is not None:
        return model_value.decode()
    elif data_value is not None:
        return data_value.decode()
    return redis_cache.IDLE


@module_exp.route('/<exp_id>/clear', methods=['DELETE'], endpoint='exp_clear')
@login_required
def exp_clear(exp_id):
    try:
        experiment = db.session.query(Experiment).filter(Experiment.id == exp_id).first()
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return ErrorResponse(500, 'Internal Database Error')
    if experiment is None:
        return ErrorResponse(400, 'Bad Request, No data')

    data_key = RedisKeyMaker.make_key(id=exp_id,
                                      type=RedisKeyMaker.DATA_PROCESSING)
    model_key = RedisKeyMaker.make_key(id=exp_id,
                                       type=RedisKeyMaker.MODEL_TRAINING)
    try:
        redis_cache.delete(model_key)
        redis_cache.delete(data_key)
    except Exception as e:
        current_app.logger.error(e)
        return ErrorResponse(500, 'Internal Server Error')
    return 'clear'


@module_exp.route('/<exp_id>/export', methods=['GET'], endpoint='exp_export')
@login_required
def exp_export(exp_id):
    code_type = request.args.get('type')
    if code_type == 'train':
        code_type = TFConverter.TYPE.TRAIN
    elif code_type == 'test':
        code_type = TFConverter.TYPE.TEST
    elif code_type == 'dataprocessing':
        code_type = TFConverter.TYPE.DATA_PROCESSING
    else:
        return ErrorResponse(400, 'Wrong type argument')

    try:
        experiment = db.session.query(Experiment).filter(Experiment.id == exp_id).first()
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        return ErrorResponse(500, 'Internal Database Error')
    if experiment is None:
        return ErrorResponse(400, 'Bad Request, No data')

    xml = pickle.loads(experiment.xml)
    xml = ''.join(xml.split('\n'))

    obj_code = None

    if code_type == TFConverter.TYPE.DATA_PROCESSING:
        try:
            data_processor = DataProcessor(xml)
            obj_code, file_ids = data_processor.generate_object_code()
            data_input_files = []
            for file_id in file_ids:
                fetched = Data.query.filter_by(id=int(file_id)).first()
                if not fetched:
                    raise SQLAlchemyError('No data in database')
                data_input_files.append(fetched.name)
            current_app.logger.info('Code was generated')
            # data_processor.run_obj_code(data_obj_code)
        except ExperimentError:
            current_app.logger.error('Invalid XML form')
            return ErrorResponse(400, 'Invalid XML form')
        except TemplateError as e:
            current_app.logger.error(e)
            return ErrorResponse(500, 'Internal Server Error, Template Error')
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            return ErrorResponse(500, 'Database Error')
        except AttributeError:
            current_app.logger.info('No data processing in XML')
        except Exception as e:
            current_app.logger.error(e)
            return ErrorResponse(500, 'Unexpected Error')
    elif code_type == TFConverter.TYPE.TRAIN or code_type == TFConverter.TYPE.TEST:
        try:
            tf_train_converter = TFConverter(xml, code_type)
            obj_code, _ = tf_train_converter.generate_object_code()
            current_app.logger.info('Code was generated')
        except ExperimentError:
            current_app.logger.error('Invalid XML form')
            return ErrorResponse(400, 'Invalid XML form')
        except TemplateError as e:
            current_app.logger.error(e)
            return ErrorResponse(500, 'Internal Server Error, Template Error')
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            return ErrorResponse(500, 'Database Error')
        except AttributeError:
            current_app.logger.info('No model in XML')
        except Exception as e:
            current_app.logger.error(e)
            return ErrorResponse(500, 'Unexpected Error')
    else:
        return ErrorResponse(400, 'Wrong type argument')

    # Fill config in model_obj_code
    if obj_code is None:
        return ErrorResponse(400, "There is no translation code for " + str(code_type))

    exported_code = link(obj_code, RunConfig())

    bytesIO = BytesIO(exported_code.encode('utf-8'))
    now_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ext = '.py'
    filename = str(exp_id) + '-' + str(code_type) + '-' + now_datetime + ext
    return send_file(bytesIO,
                     as_attachment=True,
                     attachment_filename=filename)

