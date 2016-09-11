from flask import Blueprint, render_template, \
    g, redirect, url_for

module_auth = Blueprint('auth',
                        __name__,
                        url_prefix='/auth',
                        static_folder='/static/auth',
                        template_folder='templates/auth')


@module_auth.route('/oauth2callback', methods=['GET', 'POST'], endpoint='auth_oauth2callback')
def auth_oauth2callback():
    return 'oauth2callback'


@module_auth.route('/signin/', methods=['GET', 'POST'], endpoint='auth_signin')
def auth_signin():
    return 'hello'


@module_auth.route('/login', methods=['GET', 'POST'], endpoint='auth_login')
def auth_login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    return render_template('login.html',
                           title='Sign In')


@module_auth.route('/logout', methods=['GET', 'POST'], endpoint='auth_logout')
def auth_logout():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    return render_template('login.html',
                           title='Sign In')
