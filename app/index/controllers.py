from flask import current_app, Blueprint, render_template, \
    redirect, url_for

module_index = Blueprint('index',
                        __name__,
                        url_prefix='/',
                        static_folder='/static',
                        template_folder='templates')


@module_index.route('/', methods=['GET'], endpoint='root')
def root():
    return redirect(url_for('index.index'))


@module_index.route('index', methods=['GET'], endpoint='index')
def index():
    return current_app.send_static_file('index.html')

