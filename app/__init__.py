from flask import Flask, g, render_template
from flask_login import current_user

from app.dist_task.src.dist_system.client import Client
from app.dist_task.src.dist_system.result_receiver import ResultReceiverAddress
from config import app_config
from app.mysql import DrawMLRepository
from app.redis_session import RedisSessionInterface
from app.redis import redis_cache


class Server(object):
    def __init__(self):
        self.app = Flask(__name__, static_url_path='/static')
        self.app.config.from_object(app_config)
        self.db = DrawMLRepository(self.app).db

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
        from app.test.controllers import module_test as test
        self.app.register_blueprint(index)
        self.app.register_blueprint(auth)
        self.app.register_blueprint(exp)
        self.app.register_blueprint(data)
        self.app.register_blueprint(test)

        self.client = Client(self.app.config['MASTER_ADDR'],
                             self.app.config['RESULT_ROUTER_PROTOCOL'] + '://*:' + self.app.config[
                                 'RESULT_ROUTER_PORT'],
                             ResultReceiverAddress(self.app.config['RESULT_ROUTER_PROTOCOL'],
                                                   self.app.config['RESULT_ROUTER_ADDR'],
                                                   int(self.app.config['RESULT_ROUTER_PORT'])))

    def setup_database(self):
        self.db.init_app(self.app)
        with self.app.app_context():
            self.db.create_all()

        @self.app.teardown_appcontext
        def shutdown_session(exception=None):
            DrawMLRepository().db.session.remove()

    def setup_session(self):
        # self.app.session_interface = SQLAlchemySessionInterface()
        self.app.session_interface = RedisSessionInterface()

    def setup_login_manager(self):
        from app.manager import login_manager
        login_manager.init_app(self.app)
        login_manager.login_view = 'auth.signin'

    def setup_dist_client(self):
        self.client.start()

server = Server()
server.setup_database()
server.setup_login_manager()
server.setup_dist_client()
