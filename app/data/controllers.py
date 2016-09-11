from flask import Blueprint, current_app, request, jsonify
import os

module_data = Blueprint('data',
                        __name__,
                        url_prefix='/data',
                        static_folder='/static/data',
                        template_folder='templates/data')


@module_data.route('/upload', methods=['GET'], endpoint='data_upload')
def data_upload_get():
    return current_app.send_static_file('upload.html')
    return 'upload'


@module_data.route('/upload', methods=['POST'], endpoint='data_upload_post')
def data_upload_post():
    files = request.files

    # assuming only one file is passed in the request
    # key = files.keys()[0]
    key = files.keys()
    print(key)
    print(files[key])
    value = files[key]  # this is a Werkzeug FileStorage object
    print(value)
    filename = value.filename

    if 'Content-Range' in request.headers:
        # extract starting byte from Content-Range header string
        range_str = request.headers['Content-Range']
        start_bytes = int(range_str.split(' ')[1].split('-')[0])

        # append chunk to the file on disk, or create new
        with open(filename, 'a') as f:
            f.seek(start_bytes)
            f.write(value.stream.read())

    else:
        # this is not a chunked request, so just save the whole file
        value.save(filename)

    # send response with appropriate mime type header
    return jsonify({"name": value.filename,
                    "size": os.path.getsize(filename),
                    "url": 'uploads/' + value.filename,
                    "thumbnail_url": None,
                    "delete_url": None,
                    "delete_type": None})


@module_data.route('/update', methods=['GET', 'POST'], endpoint='data_update')
def data_update():
    return 'update'


@module_data.route('/delete', methods=['GET', 'POST'], endpoint='data_delete')
def data_delete():
    return 'delete'
