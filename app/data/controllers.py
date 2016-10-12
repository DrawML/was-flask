from flask import Blueprint, request, jsonify, \
    render_template, Response, g, current_app
from flask import flash
from flask import redirect
from flask import url_for
from sqlalchemy.exc import SQLAlchemyError
from flask_login import login_required
from app.mysql import DrawMLRepository
from app.mysql_models import Data
from app.response import ErrorResponse
from app.data.models import DataManager, Refiner, ChunkRange
from datetime import datetime
import os
import json

module_data = Blueprint('data',
                        __name__,
                        url_prefix='/data',
                        static_folder='/static/data',
                        template_folder='templates/data')


@module_data.route('/api', methods=['GET'], endpoint='api_all')
@login_required
def api_all():
    db = DrawMLRepository().db
    data_set = db.session.query(Data).filter(Data.user_id == g.user.id, Data.type == 'input').all()
    return json.dumps(Refiner(data_set).get())


@module_data.route('/api/<data_id>', methods=['GET'], endpoint='api_one')
@login_required
def api_one(data_id):
    db = DrawMLRepository().db
    data = db.session.query(Data).filter(Data.user_id == g.user.id, Data.id == data_id).first()
    return json.dumps(Refiner(data).get())


@module_data.route('/upload', methods=['GET'], endpoint='upload')
@login_required
def upload():
    return render_template('data/upload.html')


@module_data.route('/', methods=['GET'], endpoint='get_all')
@login_required
def get_all():
    from config.app_config import CLOUDDFS_DOMAIN
    return render_template('/data/list.html',
                           data_set=Data.query.
                           filter_by(user_id=g.user.id, type='input')
                           .order_by(Data.date_modified.desc()).all(),
                           cloud_dfs_domain=CLOUDDFS_DOMAIN)


@module_data.route('/', methods=['POST'], endpoint='create')
@login_required
def create():
    param = request.files
    if (param is None) or (param['file'] is None):
        res = Response()
        res.status_code(400)
        res.data('Error, No parameter')
        return res
    temp_dir = os.path.join(current_app.root_path, os.pardir, 'temp_files/')
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    file = param['file']
    user_id = g.user.id
    filename = file.filename

    # [issue#4] Duplicate the name of uploaded file
    filepath = temp_dir + str(user_id) + '-' + filename

    # duplication check
    if DataManager(user_id=user_id, name=filename).check():
        return ErrorResponse(400, 'Error, Same file name already exist')

    db = DrawMLRepository().db

    if 'Content-Range' in request.headers:
        # extract starting byte from Content-Range header string
        range = ChunkRange(request.headers['Content-Range'])
        with open(filepath, 'ab') as f:
            # append chunk to the file on disk, or create new
            f.seek(range.head)
            f.write(file.stream.read())

        if range.tail == range.total:
            try:
                new_data = DataManager(name=filename, user_id=user_id, path=filepath).save()
            except SQLAlchemyError as e:
                db.session.rollback()
                current_app.logger.error(e)
                res = ErrorResponse(500, 'Error, Database internal error')
                return res
            except Exception as e:
                current_app.logger.info(e)
                return ErrorResponse(400, 'Error, File system internal error')
            finally:
                if os.path.exists(filepath):
                    os.remove(filepath)
            current_app.logger.info('Data created :' + str(new_data))

    else:
        file.save(filepath)
        try:
            new_data = DataManager(name=filename, user_id=user_id, path=filepath).save()
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(e)
            res = ErrorResponse(500, 'Error, Database internal error')
            return res
        except:
            return ErrorResponse(400, 'Error, File system internal error')
        current_app.logger.info('Data created :' + str(new_data))

    # send response with appropriate mime type header
    return 'upload'


@module_data.route('/<data_id>', methods=['GET', 'POST'], endpoint='update')
@login_required
def update(data_id):
    if request.method == 'GET':
        return render_template('/data/update.html',
                               data=Data.query.filter_by(id=data_id).first())
    name = request.form['name']

    if DataManager(user_id=g.user.id, name=name).check():
        flash('Data name ' + name + ' is duplicated', 'error')
        return redirect(url_for('data.get_all'))

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
    return redirect(url_for('data.get_all'))


@module_data.route('/<data_id>', methods=['DELETE'], endpoint='data_delete')
@login_required
def data_delete(data_id):
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
