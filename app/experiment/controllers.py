from flask import Blueprint

module_exp = Blueprint('experiment',
                       __name__,
                       url_prefix='/experiment',
                       static_folder='/static/experiment',
                       template_folder='templates/experiment')


@module_exp.route('/create', methods=['GET'], endpoint='exp_create_get')
def exp_create_get():
	return 'create'


@module_exp.route('/create', methods=['POST'], endpoint='exp_create_post')
def exp_create_post():
	return 'create'


@module_exp.route('/update', methods=['GET', 'POST'], endpoint='exp_update')
def exp_update():
	return 'update'


@module_exp.route('/delete', methods=['GET', 'POST'], endpoint='exp_delete')
def exp_delete():
	return 'delete'


@module_exp.route('/run', methods=['GET', 'POST'], endpoint='exp_run')
def exp_run():
	return 'run'


@module_exp.route('/stop', methods=['GET', 'POST'], endpoint='exp_stop')
def exp_stop():
	return 'stop'
