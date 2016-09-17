from flask import Blueprint, request, jsonify, \
    render_template, Response, g, current_app
from sqlalchemy.exc import SQLAlchemyError
from flask_login import login_required
from app.database import db
from app.db_models import Data
from app.response import ErrorResponse
from app.data.models import DataChecker, DataFetcher
import os
import json

module_data = Blueprint('data',
                        __name__,
                        url_prefix='/data',
                        static_folder='/static/data',
                        template_folder='templates/data')

FILE_SAVE_PATH = '/Users/chan/test/'


@module_data.route('/upload', methods=['GET'], endpoint='data_upload_page')
@login_required
def data_upload_page():
    return render_template('data/upload.html')


@module_data.route('', methods=['GET'], endpoint='data_get_all')
@login_required
def data_get_all():
    user_id = g.user.id
    data_set = db.session.query(Data).filter(Data.user_id == user_id).all()
    return json.dumps(data_set)     # in progress


@module_data.route('/<data_id>', methods=['GET'], endpoint='data_get')
@login_required
def data_get(data_id):
    user_id = g.user.id
    return jsonify(db.session.query(Data).filter(Data.user_id == user_id, Data.id == data_id).all())
    # in progress


@module_data.route('', methods=['POST'], endpoint='data_upload_post')
@login_required
def data_upload_post():
    param = request.files
    if (param is None) or (param['file'] is None):
        res = Response()
        res.status_code(400)
        res.data('Error, No parameter')
        return res

    file = param['file']
    user_id = g.user.id
    filename = file.filename
    filepath = FILE_SAVE_PATH + str(user_id) + '-' + filename

    if 'Content-Range' in request.headers:
        # extract starting byte from Content-Range header string
        range_str = request.headers['Content-Range']
        start_bytes = int(range_str.split(' ')[1].split('-')[0])
        if start_bytes == 0:
            data_checker = DataChecker(user_id=user_id, filename=filename)
            if data_checker.exist():
                res = ErrorResponse(400, 'Error, File already exist')
                return res
            new_data = Data(name=filename, user_id=user_id, path=filepath)
            try:
                db.session.add(new_data)
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                current_app.logger.error(e)
                res = ErrorResponse(500, 'Error, Database internal error')
                return res
            current_app.logger.info('Data created :' + str(new_data))
        # append chunk to the file on disk, or create new
        with open(filepath, 'ab') as f:
            f.seek(start_bytes)
            f.write(file.stream.read())

    else:
        # this is not a chunked request, so just save the whole file
        data_checker = DataChecker(user_id=user_id, filename=filename)
        if data_checker.exist():
            return ErrorResponse(400, 'Error, File already exist')
        new_data = Data(name=filename, user_id=user_id, path=filepath)
        try:
            db.session.add(new_data)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(e)
            return ErrorResponse(500, 'Error, Database internal error')
        current_app.logger.info('exp_data created :' + str(new_data))
        file.save(filepath)

    # send response with appropriate mime type header
    return jsonify({"name": file.filename,
                    "size": os.path.getsize(filepath),
                    "url": 'uploads/' + file.filename,
                    "thumbnail_url": None,
                    "delete_url": None,
                    "delete_type": None})


@module_data.route('/<data_id>', methods=['PATCH'], endpoint='data_update')
@login_required
def data_update(data_id):
    data_checker = DataFetcher(data_id)
    query_data = data_checker.get_data()
    if len(query_data) <= 0:
        res = ErrorResponse(400, 'Error, File does not exist')
        return res

    user_id = g.user.id
    json_data = request.get_json()
    raw = json_data['data']
    new_name = raw['name']
    new_path = FILE_SAVE_PATH + str(user_id) + '-' + new_name
    data_checker = DataChecker(user_id=user_id, filename=new_name)
    if data_checker.exist():
        return ErrorResponse(400, 'Error, File already exist')

    file_path = query_data[0].path
    try:
        os.rename(file_path, new_path)
    except Exception as e:
        current_app.logger.error(e)
        return ErrorResponse(500, 'Internal Server Error')

    updated_data = Data(name=new_name, user_id=user_id, path=new_path)
    try:
        db_result = db.session.query(Data) \
            .filter(Data.id == data_id) \
            .update(updated_data.to_dict(), synchronize_session=False)
        db.session.commit()
    except SQLAlchemyError as e:
        os.rename(new_path, file_path)
        db.session.rollback()
        current_app.logger.error(e)
        return ErrorResponse(500, 'Internal Database Error')
    current_app.logger.info('Data updated ' + str(db_result))
    return 'update'


@module_data.route('/<data_id>', methods=['DELETE'], endpoint='data_delete')
@login_required
def data_delete(data_id):
    data_checker = DataFetcher(data_id)
    query_data = data_checker.get_data()
    if len(query_data) <= 0:
        res = ErrorResponse(400, 'Error, File does not exist')
        return res
    try:
        deleted = db.session.query(Data) \
            .filter(Data.id == data_id) \
            .delete(synchronize_session=False)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return ErrorResponse(500, 'Internal Database Error')
    current_app.logger('Data removed ' + str(deleted))
    return 'delete'
