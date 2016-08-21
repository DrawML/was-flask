from database import db
from app.auth.models import OAuthSignIn
from app.dbmodels import User
from flask import Blueprint, render_template, \
	g, redirect, url_for
from flask_login import login_user, current_user

module_auth = Blueprint('auth',
                        __name__,
                        url_prefix='/auth',
                        static_folder='/static/auth',
                        template_folder='templates/auth')


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


@module_auth.route('/authorize/<provider>')
def oauth_authorize(provider):
	if not current_user.is_anonymous():
		return redirect(url_for('index'))
	oauth = OAuthSignIn.get_provider(provider)
	return oauth.authorize()


@module_auth.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    username, email = oauth.callback()
    if email is None:
        # I need a valid email address for my user identification
		# flash('Authentication failed.')
        return redirect(url_for('index'))
    # Look if the user already exists
    user = User.query.filter_by(email=email).first()
    if not user:
        # Create the user. Try and use their name returned by Google,
        # but if it is not set, split the email address at the @.
        nickname = username
        if nickname is None or nickname == "":
            nickname = email.split('@')[0]

        # We can do more work here to ensure a unique nickname, if you
        # require that.
        user=User(nickname=nickname, email=email)
        db.session.add(user)
        db.session.commit()
    # Log in the user, by default remembering them for their next visit
    # unless they log out.
    login_user(user, remember=True)
    return redirect(url_for('index'))