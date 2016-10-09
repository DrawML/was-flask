from flask import Blueprint, request, \
    render_template, g, current_app
from flask import flash
from flask import redirect
from flask import url_for
from sqlalchemy.exc import SQLAlchemyError
from flask_login import login_required
from app.mysql import DrawMLRepository
from app.mysql_models import Data
from app.response import ErrorResponse
from app.data.models import DataManager
from datetime import datetime
from app.cloud_dfs.connector import CloudDFSConnector
from config.app_config import CLOUDDFS_PORT, CLOUDDFS_ADDR


module_log = Blueprint('log',
                       __name__,
                       url_prefix='/log',
                       static_folder='/static/log',
                       template_folder='templates/log')


@module_log.route('/', methods=['GET'], endpoint='get_all')
@login_required
def get_all():
    return render_template('/log/list.html',
                           data_set=Data.query.
                           filter_by(user_id=g.user.id, type='log')
                           .order_by(Data.date_modified.desc()).all())


@module_log.route('/<data_id>', methods=['GET', 'POST'], endpoint='update')
@login_required
def update(data_id):
    if request.method == 'GET':
        data = Data.query.filter_by(id=data_id).first()
        _, f = CloudDFSConnector(ip=CLOUDDFS_ADDR, port=CLOUDDFS_PORT).\
            get_data_file(data.path)
        contents = f.split('\n')
        return render_template('/log/detail.html',
                               contents=contents, data=data)
    name = request.form['name']

    if DataManager(user_id=g.user.id, name=name).check():
        flash('Data name ' + name + ' is duplicated', 'error')
        return redirect(url_for('log.get_all'))

    data = Data.query.filter_by(id=int(data_id)).first()
    data.name = name
    data.date_modified = datetime.now()

    db = DrawMLRepository().db

    try:
        updated = db.session.query(Data)\
            .filter(Data.id == int(data_id))\
            .update(data.to_dict(), synchronize_session=False)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return ErrorResponse(500, 'Error, Database Internal Error')
    current_app.logger.info(str(updated) + ' columns updated : ' + str(data))
    flash('Data renamed')
    return redirect(url_for('log.get_all'))


@module_log.route('/<data_id>', methods=['DELETE'], endpoint='delete')
@login_required
def delete(data_id):
    query_data = DataManager(id=data_id).fetch()
    if len(query_data) <= 0:
        res = ErrorResponse(400, 'Error, File does not exist')
        return res
    try:
        DataManager(data_id).remove()
    except SQLAlchemyError as e:
        db = DrawMLRepository().db
        db.session.rollback()
        current_app.logger.error(e)
        return ErrorResponse(500, 'Internal Database Error')
    except:
        return ErrorResponse(500, 'File system Error')

    current_app.logger.info('Data removed ' + str(data_id))
    return 'delete'
