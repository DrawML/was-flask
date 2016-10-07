from flask_login import LoginManager

login_manager = LoginManager()


@login_manager.user_loader
def load_user(id):
    from app.mysql_models import User
    return User.query.get(int(id))


@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return 'unauthorized'
