from app.database import db
from flask import Flask
from config import app_config

class Server(object):
	def __init__(self):
		self.app = Flask(__name__, static_url_path='/static')
		self.app.config.from_object(app_config)

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




server = Server()
server.setup_database()
