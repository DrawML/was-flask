from flask import Blueprint, request, jsonify, \
    render_template, Response
import os

module_data = Blueprint('data',
                        __name__,
                        url_prefix='/data',
                        static_folder='/static/data',
                        template_folder='templates/data')


@module_data.route('/upload', methods=['GET'], endpoint='data_upload')
def data_upload_get():
    return render_template('data/upload.html')


@module_data.route('/upload', methods=['POST'], endpoint='data_upload_post')
def data_upload_post():
    param = request.files
    if (param is None) or (param['file'] is None):
        res = Response()
        res.status_code(400)
        res.data('Error, No parameter')
        return res

    file = param['file']
    FILE_SAVE_PATH = '/Users/chan/test/'
    filename = file.filename
    filepath = FILE_SAVE_PATH + filename

    if 'Content-Range' in request.headers:
        # extract starting byte from Content-Range header string
        range_str = request.headers['Content-Range']
        start_bytes = int(range_str.split(' ')[1].split('-')[0])
        # append chunk to the file on disk, or create new
        with open(filepath, 'ab') as f:
            f.seek(start_bytes)
            f.write(file.stream.read())

    else:
        # this is not a chunked request, so just save the whole file
        file.save(filepath)

    # send response with appropriate mime type header
    return jsonify({"name": file.filename,
                    "size": os.path.getsize(filepath),
                    "url": 'uploads/' + file.filename,
                    "thumbnail_url": None,
                    "delete_url": None,
                    "delete_type": None})


@module_data.route('/update', methods=['GET', 'POST'], endpoint='data_update')
def data_update():
    return 'update'


@module_data.route('/delete', methods=['GET', 'POST'], endpoint='data_delete')
def data_delete():
    return 'delete'
