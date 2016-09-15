from flask import Blueprint, request, current_app, render_template, g
from flask_login import login_required
import json
from jinja2.exceptions import TemplateError
from sqlalchemy import exc
from app.db_models import Experiment
from app.database import db
from app.experiment.models import Refiner, JsonParser, \
    TFConverter, TaskRunner, ExperimentError, DataProcessor


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


@module_exp.route('/<exp_id>', methods=['GET', 'POST'], endpoint='get_exp')
@login_required
def get_exp(exp_id):
    # experiment = Experiment.query.get(int(exp_id))
    experiment = db.session.query(Experiment).filter(Experiment.id == exp_id).all()
    refined_exps = Refiner(experiment)
    current_app.logger.info('GET exp <%r>', refined_exps.exps[0]['name'])
    return json.dumps(refined_exps.exps)


@module_exp.route('/', methods=['POST'], endpoint='exp_create')
@login_required
def exp_create():
    json_data = request.get_json()
    exp_data = JsonParser.parse_post(json_data, g.user.id)
    if type(exp_data) != Experiment:
        current_app.logger.error(exp_data)
        return 'json key error'

    try:
        experiments = db.session.query(Experiment) \
            .filter(Experiment.user_id == exp_data.user_id,
                    Experiment.name == exp_data.name).all()
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return 'create error'
    if len(experiments) > 0:
        return 'duplicated exp name'

    try:
        db.session.add(exp_data)
        db.session.commit()
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return 'create error'
    current_app.logger.info('exp_data created :' + exp_data.name + ' ' + exp_data.user.user_id)
    return 'created'


@module_exp.route('/<exp_id>', methods=['PATCH'], endpoint='exp_update')
@login_required
def exp_update(exp_id):
    json_data = request.get_json()
    exp_data = JsonParser.parse_post(json_data, g.user.id)
    if type(exp_data) != Experiment:
        current_app.logger.error(exp_data)
        return 'json key error'

    try:
        experiments = db.session.query(Experiment) \
            .filter(Experiment.user_id == exp_data.user_id,
                    Experiment.name == exp_data.name).all()
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return 'read error'
    if len(experiments) > 0:
        return 'duplicated exp name'

    updated = db.session.query(Experiment)\
        .filter(Experiment.id == exp_id)\
        .update(exp_data.to_dict(), synchronize_session=False)
    db.session.commit()
    current_app.logger.info(str(updated) + ' columns updated : ' + exp_data.name)
    return 'updated'


@module_exp.route('/<exp_id>', methods=['DELETE'], endpoint='exp_delete')
@login_required
def exp_delete(exp_id):
    deleted = db.session.query(Experiment) \
        .filter(Experiment.id == exp_id) \
        .delete(synchronize_session=False)
    db.session.commit()
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
        current_app.logger.error("Invalid XML form")
        return "invalid XML form"
    except TemplateError as e:
        current_app.logger.error(e)
        return "Template Error"
    except AttributeError:
        current_app.logger.info("No data processing in XML")
    except Exception as e:
        current_app.logger.error(e)
        return "Unexpected Error"

    # run data processing
    # we should pass data id argument to taskrunner
    # if error occur while processing : return error

    try:
        tf_converter = TFConverter(xml)
        obj_code = tf_converter.generate_object_code()
        current_app.logger.info("Code was generated")
        tf_converter.run_obj_code(obj_code)
    except ExperimentError:
        current_app.logger.error("Invalid XML form")
        return "invalid XML form"
    except TemplateError as e:
        current_app.logger.error(e)
        return "Template Error"
    except AttributeError:
        current_app.logger.info("No model in XML")
    except Exception as e:
        current_app.logger.error(e)
        return "Unexpected Error"

    # we should pass data id argument to taskrunner
    # tr = TaskRunner(obj_code)
    # ..............
    return 'run'


@module_exp.route('/stop', methods=['GET', 'POST'], endpoint='exp_stop')
@login_required
def exp_stop():
    return 'stop'
