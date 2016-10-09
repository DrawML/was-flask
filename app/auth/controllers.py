from flask import Blueprint, render_template, make_response, \
    redirect, url_for, request, current_app, flash, session
from flask_login import login_user, logout_user
from sqlalchemy.exc import SQLAlchemyError
from app.mysql_models import User
from app.mysql import DrawMLRepository

module_auth = Blueprint('auth',
                        __name__,
                        url_prefix='/auth',
                        static_folder='/static/auth',
                        template_folder='templates')


@module_auth.route('/register', methods=['GET', 'POST'])
def register():
    db = DrawMLRepository().db

    if request.method == 'GET':
        return render_template('auth/register.html')
    user = User(request.form['user_id'], request.form['pw'])
    try:
        duplicate = db.session.query(User).filter(User.user_id == user.user_id).all()
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        flash('Internal Server Error', 'error')
        return render_template('auth/register.html')
    if len(duplicate) > 0:
        flash('Username "' + user.user_id + '" is duplicated', 'error')
        return render_template('auth/register.html')
    try:
        db.session.add(user)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        flash('Internal Server Error', 'error')
        return render_template('auth/register.html')
    current_app.logger.info('User ' + str(user) + ' successfully registered')
    return redirect(url_for('auth.signin'))


@module_auth.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'GET':
        return render_template('auth/signin.html')
    user_id = request.form["user_id"]
    pw = request.form['pw']
    remember_me = False
    if 'remember_me' in request.form:
        remember_me = True
    registered_user = User.query.filter_by(user_id=user_id, pw=pw).first()
    if registered_user is None:
        flash('Username or Password is invalid', 'error')
        return redirect(url_for('auth.signin'))
    login_user(registered_user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index.root'))


@module_auth.route('/signout')
def signout():
    session.clear()
    logout_user()
    return redirect(url_for('index.root'))
