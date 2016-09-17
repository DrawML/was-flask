from flask import Blueprint, request, jsonify, \
    render_template, Response, g, current_app
from sqlalchemy.exc import SQLAlchemyError
from flask_login import login_required
from app.database import db
from app.db_models import Data
from app.response import ErrorResponse
from app.data.models import DataChecker
import os

module_data = Blueprint('data',
                        __name__,
                        url_prefix='/data',
                        static_folder='/static/data',
                        template_folder='templates/data')


@module_data.route('/upload', methods=['GET'], endpoint='data_upload')
@login_required
def data_upload_get():
    return render_template('data/upload.html')


@module_data.route('/upload', methods=['POST'], endpoint='data_upload_post')
@login_required
def data_upload_post():
    param = request.files
    if (param is None) or (param['file'] is None):
        res = Response()
        res.status_code(400)
        res.data('Error, No parameter')
        return res

    file = param['file']
    FILE_SAVE_PATH = '/Users/chan/test/'
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
        current_app.logger.info('exp_data created :' + str(new_data))
        file.save(filepath)

    # send response with appropriate mime type header
    return jsonify({"name": file.filename,
                    "size": os.path.getsize(filepath),
                    "url": 'uploads/' + file.filename,
                    "thumbnail_url": None,
                    "delete_url": None,
                    "delete_type": None})


@module_data.route('/update', methods=['GET', 'POST'], endpoint='data_update')
@login_required
def data_update():
    return 'update'


@module_data.route('/delete', methods=['GET', 'POST'], endpoint='data_delete')
@login_required
def data_delete():
    return 'delete'
