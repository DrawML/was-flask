from flask import Blueprint, request, current_app
import json
from sqlalchemy import exc
from db_models import Experiment
from database import db
from app.experiment.models import exp_refiner

module_exp = Blueprint('experiment',
                       __name__,
                       url_prefix='/experiment',
                       static_folder='/static/experiment',
                       template_folder='templates/experiment')


@module_exp.route('/<user_id>', methods=['GET', 'POST'], endpoint='exp')
@module_exp.route('/', defaults={'user_id': 'index'})
def exp(user_id):
	experiments = db.session.query(Experiment).filter(Experiment.user_id == user_id).all()
	refined_exps = exp_refiner(experiments)
	json.dumps(refined_exps.exps)
	current_app.logger.info('exp for ' + user_id + ' : ' + str(len(experiments)))
	return json.dumps(refined_exps.exps)


@module_exp.route('/create', methods=['GET'], endpoint='exp_create_get')
def exp_create_get():
	return 'create'


@module_exp.route('/create', methods=['POST'], endpoint='exp_create_post')
def exp_create_post():
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


@module_exp.route('/update', methods=['POST'], endpoint='exp_update_post')
def exp_update_post():
	json_data = request.get_json()
	exp_json = json_data['exp_data']
	exp_name = json_data['exp_name']
	exp_data = Experiment(exp_json['name'],
	                      exp_json['user_id'],
	                      bytes(exp_json['xml'], 'utf-8'),
	                      bytes(exp_json['drawing'], 'utf-8'),
	                      exp_json['input'])
	updated = db.session.query(Experiment)\
		.filter(Experiment.user_id == exp_data.user_id, Experiment.name == exp_name)\
		.update(exp_data.to_dict(), synchronize_session=False)
	db.session.commit()
	current_app.logger.info(str(updated) + ' columns updated : ' + exp_data.name + ' ' + exp_data.user_id)
	return 'updated'


@module_exp.route('/delete', methods=['GET', 'POST'], endpoint='exp_delete')
def exp_delete():
	json_data = request.get_json()
	exp_json = json_data['exp_data']
	deleted = db.session.query(Experiment) \
		.filter(Experiment.user_id == exp_json['user_id'], Experiment.name == exp_json['name']) \
		.delete(synchronize_session=False)
	db.session.commit()
	current_app.logger.info(str(deleted) + ' columns deleted : ' + exp_json['name'] + ' ' + exp_json['user_id'])
	return 'delete'


@module_exp.route('/run', methods=['GET', 'POST'], endpoint='exp_run')
def exp_run():
	return 'run'


@module_exp.route('/stop', methods=['GET', 'POST'], endpoint='exp_stop')
def exp_stop():
	return 'stop'
