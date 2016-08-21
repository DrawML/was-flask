from flask import Blueprint

module_data = Blueprint('data',
                        __name__,
                        url_prefix='/data',
                        static_folder='/static/data',
                        template_folder='templates/data')


@module_data.route('/upload', methods=['GET', 'POST'], endpoint='data_upload')
def data_upload():
	return 'upload'


@module_data.route('/update', methods=['GET', 'POST'], endpoint='data_update')
def data_update():
	return 'update'


@module_data.route('/delete', methods=['GET', 'POST'], endpoint='data_delete')
def data_delete():
	return 'delete'
