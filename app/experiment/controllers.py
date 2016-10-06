import json

from flask import Blueprint, request, current_app, render_template, g
from flask_login import login_required
from jinja2.exceptions import TemplateError
from sqlalchemy.exc import SQLAlchemyError

from app.common.object_code.util import ExperimentError, DataProcessor, TaskRunner, TFConverter
from app.dist_task.src.dist_system.client import Client
from app.experiment.models import Refiner, JsonParser
from app.mysql import db
from app.mysql_models import Experiment
from app.redis import redis_cache, RedisKeyMaker
from app.response import ErrorResponse

module_exp = Blueprint('experiment',
                       __name__,
                       url_prefix='/experiments',
                       static_folder='/static/experiments',
                       template_folder='templates/experiments')


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


@module_exp.route('/<exp_id>', methods=['GET'], endpoint='get_exp')
@login_required
def get_exp(exp_id):
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
        updated = db.session.query(Experiment)\
            .filter(Experiment.id == exp_id)\
            .update(exp_data.to_dict(), synchronize_session=False)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return ErrorResponse(500, 'Error, Database Internal Error')
    current_app.logger.info(str(updated) + ' columns updated : ' + str(exp_data))
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
    xml = request.data.decode()

    data_obj_code = None
    data_input_files = None
    try:
        data_processor = DataProcessor(xml)
        data_obj_code, data_input_files = data_processor.generate_object_code()
        current_app.logger.info('Code was generated')
        # data_processor.run_obj_code(data_obj_code)
    except ExperimentError:
        current_app.logger.error('Invalid XML form')
        return ErrorResponse(400, 'Invalid XML form')
    except TemplateError as e:
        current_app.logger.error(e)
        return ErrorResponse(500, 'Internal Server Error, Template Error')
    except AttributeError:
        current_app.logger.info('No data processing in XML')
    except Exception as e:
        current_app.logger.error(e)
        return ErrorResponse(500, 'Unexpected Error')

    data_key = RedisKeyMaker.make_key(id=exp_id,
                                      type=RedisKeyMaker.DATA_PROCESSING)
    model_obj_code = None
    model_input_file = None
    try:
        tf_train_converter = TFConverter(xml, TFConverter.TYPE.TRAIN)
        model_obj_code, model_input_file = tf_train_converter.generate_object_code()
        current_app.logger.info('Code was generated')
        # tf_converter.run_obj_code(model_obj_code)
    except ExperimentError:
        current_app.logger.error('Invalid XML form')
        return ErrorResponse(400, 'Invalid XML form')
    except TemplateError as e:
        current_app.logger.error(e)
        return ErrorResponse(500, 'Internal Server Error, Template Error')
    except AttributeError:
        current_app.logger.info('No model in XML')
    except Exception as e:
        current_app.logger.error(e)
        return ErrorResponse(500, 'Unexpected Error')

    model_key = RedisKeyMaker.make_key(id=exp_id,
                                       type=RedisKeyMaker.MODEL_TRAINING)
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
    data_key = RedisKeyMaker.make_key(id=exp_id,
                                      type=RedisKeyMaker.DATA_PROCESSING)
    model_key = RedisKeyMaker.make_key(id=exp_id,
                                       type=RedisKeyMaker.MODEL_TRAINING)
    data_value = redis_cache.get(data_key).decode()
    if data_value is not None:
        if data_value == redis_cache.RUNNING:
            Client().request_cancel(data_key)
            # redis_cache.set(data_key, redis_cache.CANCEL)
            return 'task was canceled'

    model_value = redis_cache.get(model_key).decode()
    if model_value is not None:
        if model_value == redis_cache.RUNNING:
            Client().request_cancel(model_key)
            # redis_cache.set(model_key, redis_cache.CANCEL)
            return 'task was canceled'

    return 'Nothing changed'


@module_exp.route('/<exp_id>/status', methods=['GET'], endpoint='exp_status')
@login_required
def exp_status(exp_id):
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
    return 'No status'


@module_exp.route('/<exp_id>/clear', methods=['DELETE'], endpoint='exp_clear')
@login_required
def exp_clear(exp_id):
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
