from flask import Blueprint, request, current_app
import json
from sqlalchemy import exc
from app.db_models import Experiment
from app.database import db
from app.experiment.models import Refiner, JsonParser, \
	TFConverter, TaskRunner, ExperimentError, DataProcessor


module_exp = Blueprint('experiment',
                       __name__,
                       url_prefix='/experiment',
                       static_folder='/static/experiment',
                       template_folder='templates/experiment')


@module_exp.route('/<user_id>', methods=['GET', 'POST'], endpoint='user_all_exp')
@module_exp.route('/', defaults={'user_id': 'index'})
def user_all_exp(user_id):
	experiments = db.session.query(Experiment).filter(Experiment.user_id == user_id).all()
	refined_exps = Refiner(experiments)
	json.dumps(refined_exps.exps)
	current_app.logger.info('exp for ' + user_id + ' : ' + str(len(experiments)))
	return json.dumps(refined_exps.exps)


@module_exp.route('/<user_id>/<exp_name>', methods=['GET', 'POST'], endpoint='user_exp')
@module_exp.route('/', defaults={'user_id': 'index', 'exp_name': ''})
def user_exp(user_id, exp_name):
	experiments = db.session.query(Experiment).\
		filter(Experiment.user_id == user_id, Experiment.name == exp_name).all()
	refined_exps = Refiner(experiments)
	json.dumps(refined_exps.exps)
	current_app.logger.info('exp for ' + user_id + ' : ' + str(len(experiments)))
	return json.dumps(refined_exps.exps)


@module_exp.route('/', methods=['POST'], endpoint='exp_create')
def exp_create():
	json_data = request.get_json()
	exp_data = JsonParser.parse_post(json_data)
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
	current_app.logger.info('exp_data created :' + exp_data.name + ' ' + exp_data.user_id)
	return 'created'


@module_exp.route('/<user_id>/<exp_name>', methods=['PATCH'], endpoint='exp_update')
@module_exp.route('/<user_id>/<exp_name>', defaults={'user_id': 'index', 'exp_name': ''})
def exp_update(user_id, exp_name):
	json_data = request.get_json()

	try:
		exp_json = json_data['exp_data']
		exp_data = Experiment(exp_json['name'],
		                      exp_json['user_id'],
		                      exp_json['xml'].encode(),
		                      exp_json['drawing'].encode(),
		                      exp_json['input'])
	except KeyError as e:
		current_app.logger.error(e)
		return 'json key error'
	updated = db.session.query(Experiment)\
		.filter(Experiment.user_id == user_id, Experiment.name == exp_name)\
		.update(exp_data.to_dict(), synchronize_session=False)
	db.session.commit()
	current_app.logger.info(str(updated) + ' columns updated : ' + exp_data.name + ' ' + exp_data.user_id)
	return 'updated'


@module_exp.route('/<user_id>/<exp_name>', methods=['DELETE'], endpoint='exp_delete')
@module_exp.route('/<user_id>/<exp_name>', defaults={'user_id': 'index', 'exp_name': ''})
def exp_delete(user_id, exp_name):
	deleted = db.session.query(Experiment) \
		.filter(Experiment.user_id == user_id, Experiment.name == exp_name) \
		.delete(synchronize_session=False)
	db.session.commit()
	current_app.logger.info(str(deleted) + ' columns deleted : ' + user_id + ' ' + exp_name)
	return 'delete'


@module_exp.route('/run', methods=['POST'], endpoint='exp_run')
def exp_run():
	xml = request.data.decode()

	try:
		data_processor = DataProcessor(xml)
	except ExperimentError:
		current_app.logger.error("Invalid XML form")
		return "invalid XML form"
	except AttributeError:
		current_app.logger.info("No data processing in XML")

	try:
		tf_converter = TFConverter(xml)
		obj_code = tf_converter.generate_object_code()
		current_app.logger.info("Code was generated")
		tf_converter.run_obj_code(obj_code)
	except ExperimentError:
		current_app.logger.error("Invalid XML form")
		return "invalid XML form"
	except AttributeError:
		current_app.logger.info("No model in XML")
	# tr = TaskRunner(obj_code)
	# ..............

	return 'run'


@module_exp.route('/stop', methods=['GET', 'POST'], endpoint='exp_stop')
def exp_stop():
	return 'stop'
