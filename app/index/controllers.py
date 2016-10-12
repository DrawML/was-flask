from flask import Blueprint, render_template, \
    redirect, url_for, g
from app.mysql_models import Experiment
from flask_login import login_required

module_index = Blueprint('index',
                         __name__,
                         url_prefix='/',
                         static_folder='/static',
                         template_folder='templates')


@module_index.route('/', methods=['GET'], endpoint='root')
@login_required
def root():
    return redirect(url_for('index.index'))


@module_index.route('index', methods=['GET'], endpoint='index')
@login_required
def index():
    return render_template("index.html")
