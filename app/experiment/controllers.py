from flask import Blueprint

module_exp = Blueprint('experiment',
                       __name__,
                       url_prefix='/expreiment',
                       static_folder='/static/experiment',
                       template_folder='templates/experiment')


@module_exp.route('/create', methods=['GET'])
def exp_create_get():
	return 'create'


@module_exp.route('/create', methods=['POST'])
def exp_create_post():
	return 'create'


@module_exp.route('/update', methods=['GET', 'POST'])
def exp_update():
	return 'update'


@module_exp.route('/delete', methods=['GET', 'POST'])
def exp_delete():
	return 'delete'


@module_exp.route('/run', methods=['GET', 'POST'])
def exp_run():
	return 'run'


@module_exp.route('/stop', methods=['GET', 'POST'])
def exp_stop():
	return 'stop'
