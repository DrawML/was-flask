from flask import Flask, g, render_template
from flask_login import current_user
from config import app_config
from app.session import SQLAlchemySessionInterface
from app.database import db
from app.manager import login_manager


class Server(object):
    def __init__(self):
        self.app = Flask(__name__, static_url_path='/static')
        self.app.config.from_object(app_config)

        @self.app.before_request
        def before_request():
            g.user = current_user

        @self.app.errorhandler(404)
        def not_found(error):
            return render_template('404.html')
        """
            routing
            import modules and components and
            register blueprints
        """
        from app.index.controllers import module_index as index
        from app.auth.controllers import module_auth as auth
        from app.experiment.controllers import module_exp as exp
        from app.data.controllers import module_data as data
        self.app.register_blueprint(index)
        self.app.register_blueprint(auth)
        self.app.register_blueprint(exp)
        self.app.register_blueprint(data)

    def setup_database(self):
        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()

        @self.app.teardown_appcontext
        def shutdown_session(exception=None):
            db.session.remove()

    def setup_session(self):
        self.app.session_interface = SQLAlchemySessionInterface()

    def setup_login_manager(self):
        login_manager.init_app(self.app)
        login_manager.login_view = 'auth.signin'

server = Server()
server.setup_database()
server.setup_login_manager()
