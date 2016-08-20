from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')

"""
	routing
	import modules and components and
	register blueprints
"""
# from app.mod_name.controllers import mod_name
# app.register_blueprint(mod_name)
# ..


# database
db = SQLAlchemy(app)
db.create_all()


@app.errorhandler(404)
def not_found(error):
	return render_template('404.html')
