from flask import Blueprint, request, current_app, render_template, g
from flask_login import login_required
import json
from jinja2.exceptions import TemplateError
from sqlalchemy.exc import SQLAlchemyError
from app.mysql_models import Experiment
from app.mysql import db
from app.experiment.models import Refiner, JsonParser, \
    TFConverter, TaskRunner, ExperimentError, DataProcessor
from app.response import ErrorResponse

from app.dist_task.src.dist_system.client import Client

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


@module_exp.route('/run', methods=['POST'], endpoint='exp_run')
@login_required
def exp_run():
    xml = request.data.decode()

    try:
        data_processor = DataProcessor(xml)
        obj_code = data_processor.generate_object_code()
        data_processor.run_obj_code(obj_code)
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

    # run data processing
    # we should pass data id argument to taskrunner
    # if error occur while processing : return error

    try:
        tf_converter = TFConverter(xml)
        obj_code = tf_converter.generate_object_code()
        current_app.logger.info('Code was generated')
        tf_converter.run_obj_code(obj_code)
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

    # we should pass data id argument to taskrunner
    # tr = TaskRunner(obj_code)
    # ..............

    # # Callback parameter
    # <status>
    #   - ["success", "error", "cancel"]: str
    # <body>
    #   - dict      when "success",
    #       { "stdout", "stderr", "result_file_token" }
    #   - str       when "error"
    #   - None      when "cancel"
    def create_callback():
        now_user_id = g.user.id

        def _callback(status: str, body=None):
            print('[run_experiment] ', 'callbacked! ')

            if status == 'success':
                print("[%d] callback is called with 'success'" % now_user_id)
            elif status == 'error':
                print("[%d] callback is called with 'fail'" % now_user_id)
            elif status == 'cancel':
                print("[%d] callback is called with 'cancel1'" % now_user_id)

            if body is not None:
                print(body['stderr'])

        return _callback

    input_path = 'app/experiment/object_code/test/linear_regression_input.txt'

    def get_dummy_input(input_path: str):
        with open(input_path, 'r', encoding='utf-8') as f:
            return f.read()

    # when request DataProcessingTask
    data_processing_task_job_dict = dict()
    data_processing_task_job_dict['data_file_num'] = 2
    data_processing_task_job_dict['data_file_token_list'] = ['DUMMY_TOKEN1', 'DUMMY_TOKEN1']
    data_processing_task_job_dict['object_code'] = obj_code
    Client().request_task(g.experiment.id, Client.TaskType.TYPE_DATA_PROCESSING_TASK, data_processing_task_job_dict,
                          create_callback())

    # when request TensorflowTask
    tensorflow_task_job_dict = dict()
    tensorflow_task_job_dict['data_file_token'] = get_dummy_input(input_path)
    tensorflow_task_job_dict['object_code'] = obj_code
    Client().request_task(g.experiment.id, Client.TaskType.TYPE_TENSORFLOW_TASK, tensorflow_task_job_dict,
                          create_callback())

    # when request cancel experiment
    Client().request_cancel(g.experiment.id)

    return 'run'


@module_exp.route('/stop', methods=['GET', 'POST'], endpoint='exp_stop')
@login_required
def exp_stop():
    return 'stop'
