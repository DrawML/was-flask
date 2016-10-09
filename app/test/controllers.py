import pickle
from datetime import datetime

from flask import Blueprint, request, current_app, render_template, g, \
    flash, redirect, url_for
from flask_login import login_required
from jinja2.exceptions import TemplateError
from sqlalchemy.exc import SQLAlchemyError

from app.common.object_code.util import TFConverter, TestError, TaskRunner
from app.dist_task.src.dist_system.client import Client
from app.mysql import DrawMLRepository
from app.mysql_models import TrainedModel, Data
from app.redis import redis_cache, RedisKeyMaker
from app.response import ErrorResponse

module_test = Blueprint('test',
                        __name__,
                        url_prefix='/tests',
                        static_folder='/static',
                        template_folder='templates/test')
db = DrawMLRepository().db


@module_test.route('/', methods=['GET'], endpoint='get_all_model')
@login_required
def get_all_model():
    return render_template('/test/list.html',
                           models=TrainedModel.query.
                           filter_by(user_id=g.user.id).order_by(TrainedModel.date_modified.desc()).all())


@module_test.route('/<model_id>', methods=['GET'], endpoint='get_model')
@login_required
def get_model(model_id):
    status = redis_cache.IDLE
    model_key = RedisKeyMaker.make_key(id=model_id,
                                       type=RedisKeyMaker.MODEL_TESTING)
    model_value = redis_cache.get(model_key)
    if model_value is not None:
        status = model_value.decode()
    print(status)
    return render_template('/test/detail.html',
                           datas=Data.query.
                           filter_by(user_id=g.user.id, type='input').order_by(Data.date_modified.desc()).all(),
                           model=TrainedModel.query.filter_by(id=model_id).first(),
                           status=status)


@module_test.route('/<model_id>/update', methods=['GET', 'POST'], endpoint='update_model')
@login_required
def update_model(model_id):
    if request.method == 'GET':
        return render_template('/test/update.html',
                               model=TrainedModel.query.filter_by(id=model_id).first())
    name = request.form['name']
    try:
        duplicate = TrainedModel.query.filter_by(user_id=g.user.id,
                                                 name=name).all()
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        flash('Internal Server Error', 'error')
        return redirect(url_for('test.get_all_model'))
    if len(duplicate) > 0:
        flash('Model name ' + name + ' is duplicated', 'error')
        return redirect(url_for('test.get_all_model'))

    model = TrainedModel.query.filter_by(id=int(model_id)).first()
    model.name = name
    model.date_modified = datetime.now()
    try:
        updated = db.session.query(TrainedModel)\
            .filter(TrainedModel.id == int(model_id))\
            .update(model.to_dict(), synchronize_session=False)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return ErrorResponse(500, 'Error, Database Internal Error')
    current_app.logger.info(str(updated) + ' columns updated : ' + str(model))
    flash('Trained model renamed')
    return redirect(url_for('test.get_all_model'))


@module_test.route('/<model_id>', methods=['DELETE'], endpoint='model_delete')
@login_required
def model_delete(model_id):
    try:
        deleted = db.session.query(TrainedModel) \
            .filter(TrainedModel.id == int(model_id)) \
            .delete(synchronize_session=False)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        flash('Database Internal Error', 'Error')
        return redirect(url_for('test.get_all_model'))
    current_app.logger.info(str(deleted) + ' columns deleted : ' + str(model_id))
    return 'deleted'


@module_test.route('/<model_id>/<data_id>', methods=['POST'], endpoint='test_run')
@login_required
def test_run(model_id, data_id):
    print('sasdfa')
    model = TrainedModel.query.filter_by(id=int(model_id)).first()
    xml = pickle.loads(model.xml)

    model_key = RedisKeyMaker.make_key(id=model_id,
                                       type=RedisKeyMaker.MODEL_TESTING)
    if redis_cache.get(model_key) == redis_cache.RUNNING:
        return ErrorResponse(400, 'Test is running now')

    model_obj_code = None
    try:
        tf_converter = TFConverter(xml, TFConverter.TYPE.TEST)
        model_obj_code, dummy = tf_converter.generate_object_code()
        model_input_file = Data.query.filter_by(id=int(data_id)).first().path
        current_app.logger.info('Test code was generated')
        # tf_converter.run_obj_code(model_obj_code)
    except TestError:
        current_app.logger.error('Invalid XML form')
        return ErrorResponse(400, 'Invalid XML form')
    except TemplateError as e:
        current_app.logger.error(e)
        return ErrorResponse(500, 'Internal Server Error, Template Error')
    except AttributeError:
        current_app.logger.info('No model in XML')
    except Exception as e:
        current_app.logger.error(e)
        return ErrorResponse(500, 'Unexpected Error')
    model_session_file = model.path
    valid = TaskRunner(user_id=g.user.id,
                       test_obj_code=model_obj_code,
                       test_input_file=model_input_file,
                       test_session_file=model_session_file,
                       test_key=model_key).run()
    if valid is False:
        return 'invalid request task is not done'
    return 'run'


@module_test.route('/<model_id>/stop', methods=['DELETE'], endpoint='test_stop')
@login_required
def test_stop(model_id):
    model_key = RedisKeyMaker.make_key(id=model_id,
                                       type=RedisKeyMaker.MODEL_TESTING)
    model_value = redis_cache.get(model_key)
    if not model_value:
        flash('Error, No cache status')
        return redirect(url_for('test.get_all_model'))
    model_value = model_value.decode()
    if model_value is not None:
        if model_value == redis_cache.RUNNING:
            Client().request_cancel(model_key)
            # redis_cache.set(model_key, redis_cache.CANCEL)
            flash('task was canceled')
    return redirect(url_for('test.get_model', model_id=model_id))


@module_test.route('/<model_id>/status', methods=['GET'], endpoint='test_status')
@login_required
def test_status(model_id):
    model_key = RedisKeyMaker.make_key(id=model_id,
                                       type=RedisKeyMaker.MODEL_TESTING)
    model_value = redis_cache.get(model_key)
    if model_value is not None:
        return model_value.decode()
    return 'No status'


@module_test.route('/<model_id>/clear', methods=['DELETE'], endpoint='model_clear')
@login_required
def model_clear(model_id):
    model_key = RedisKeyMaker.make_key(id=model_id,
                                       type=RedisKeyMaker.MODEL_TESTING)
    try:
        redis_cache.delete(model_key)
    except Exception as e:
        current_app.logger.error(e)
        flash('Internal Server Error')
        return redirect(url_for('test.get_all_model'))
    flash('Cache cleared')
    return redirect(url_for('test.get_all_model'))
