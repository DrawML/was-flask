from database import db
import datetime
# Base = declarative_base()


class Base(db.Model):
	__abstract__  = True

	id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
	date_created  = db.Column(db.DateTime, default=datetime.datetime.now())
	date_modified = db.Column(db.DateTime, default=datetime.datetime.now(),
	                          onupdate=datetime.datetime.now())


class User(Base):
	__tablename__ = 'user'
	user_id        = db.Column(db.VARCHAR(64), nullable=False)
	pw            = db.Column(db.VARCHAR(64))

	def __init__(self, userid, pw):
		self.user_id = userid
		self.pw = pw

	def __repr__(self):
		return '<User %r>' % (self.name)


class Experiment(Base):
	__tablename__ = 'experiment'
	name = db.Column(db.VARCHAR(45), primary_key=True)
	user_id = db.Column(db.VARCHAR(45), db.ForeignKey('user.id'), primary_key=True)
	xml = db.Column(db.BLOB)
	drawing = db.Column(db.BLOB)
	input = db.Column(db.Integer)

	def __init__(self, name, user_id, xml, drawing, input):
		super()
		self.name = name
		self.user_id = user_id
		self.xml = xml
		self.drawing = drawing
		self.input = input

	def __repr__(self):
		return '<Experiment %r>' % (self.user)

	def to_dict(self):
		return {
			Experiment.name: self.name,
			Experiment.user_id: self.user_id,
			Experiment.xml: self.xml,
			Experiment.drawing: self.drawing,
			Experiment.input: self.input
		}


class Test(db.Model):
	__tablename__ = 'test'
	idtest = db.Column(db.Integer, autoincrement=True, primary_key=True)
	text = db.Column(db.VARCHAR(45))

	def __init__(self, text):
		self.text = text

	def __repr__(self):
		return '<Test %r>' % (self.user)

