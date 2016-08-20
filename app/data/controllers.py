from flask import Blueprint

module_data = Blueprint('data',
                        __name__,
                        url_prefix='/data',
                        static_folder='/static/data',
                        template_folder='templates/data')


@module_data.route('/upload', methods=['GET', 'POST'])
def exp_update():
	return 'upload'


@module_data.route('/update', methods=['GET', 'POST'])
def exp_delete():
	return 'update'


@module_data.route('/delete', methods=['GET', 'POST'])
def exp_run():
	return 'delete'
