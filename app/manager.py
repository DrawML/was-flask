from flask_login import LoginManager
from app.mysql_models import User

login_manager = LoginManager()


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return 'unauthorized'
