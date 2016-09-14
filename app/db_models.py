from app.database import db
import datetime
# Base = declarative_base()


class Base(db.Model):
    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_created  = db.Column(db.DateTime, default=datetime.datetime.now())
    date_modified = db.Column(db.DateTime, default=datetime.datetime.now(),
                              onupdate=datetime.datetime.now())


class User(Base):
    __tablename__   = 'user'
    __table_args__  = {'extend_existing': True}
    user_id         = db.Column(db.VARCHAR(64), nullable=False)
    pw              = db.Column(db.VARCHAR(64))

    def __init__(self, userid, pw):
        self.user_id = userid
        self.pw = pw

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User %r>' % self.user_id


class Experiment(Base):
    __tablename__   = 'experiment'
    __table_args__  = {'extend_existing': True}
    name            = db.Column(db.VARCHAR(45), primary_key=True)
    user_id         = db.Column(db.VARCHAR(45), db.ForeignKey('user.user.id'), primary_key=True)
    xml             = db.Column(db.BLOB)
    drawing         = db.Column(db.BLOB)
    input           = db.Column(db.Integer)

    def __init__(self, name, user_id, xml, drawing, input):
        super()
        self.name       = name
        self.user_id    = user_id
        self.xml        = xml
        self.drawing    = drawing
        self.input      = input

    def __repr__(self):
        return '<Experiment %r %r>' % (self.user_id, self.name)

    def to_dict(self):
        return {
            Experiment.name:    self.name,
            Experiment.user_id: self.user_id,
            Experiment.xml:     self.xml,
            Experiment.drawing: self.drawing,
            Experiment.input:   self.input
        }


class FlaskSession():
    __tablename__ = 'session'
    __table_args__ = {'extend_existing': True}
    sid     = db.Column(db.VARCHAR(45), primary_key=True)
    value   = db.Column(db.BLOB)

    def __init__(self, sid, value):
        super()
        self.sid     = sid
        self.value  = value

    def __repr__(self):
        return '<FlaskSession %r>' % self.sid

    @staticmethod
    def change(cls, sid, value):
        rec = db.session.query(cls).filter(cls.sid == sid).first()
        if not rec:
            rec = cls()
            rec.sid = sid
        rec.value = value
        return rec
