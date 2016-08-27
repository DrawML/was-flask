from database import db, Base


class Experiment(Base):
	_tablename = 'experiment'
	user    = db.Column(db.VARCHAR(45), nullable=False)
	drawing = db.Column(db.BLOB)
	xml     = db.Column(db.BLOB)
	input   = db.Column(db.INT)

	def __init__(self, user, drawing, xml, input):
		self.user = user
		self.drawing = drawing
		self.xml = xml
		self.input = input

