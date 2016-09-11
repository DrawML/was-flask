from werkzeug.datastructures import CallbackDict
from uuid import uuid4
import pickle
from flask.sessions import SessionInterface, SessionMixin
from app.database import db
from app.db_models import FlaskSession


class SQLAlchemySession(CallbackDict, SessionMixin):

    def __init__(self, initial=None, sid=None, new=False):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False


class SQLAlchemySessionInterface(SessionInterface):
    session_class = SQLAlchemySession
    serializer = pickle

    def generate_sid(self):
        return str(uuid4())

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            sid = self.generate_sid()
            return self.session_class(sid=sid, new=True)

        rec = db.session.query(FlaskSession).\
            filter(FlaskSession.sid == sid).first()
        if rec is None:
            return self.session_class(sid=sid, new=True)
        data = self.serializer.loads(rec.value)
        return self.session_class(data, sid=sid)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)

        if not session:
            rec = db.session.query(FlaskSession).filter(FlaskSession.sid == session.sid).first()
            db.session.delete(rec)
            db.session.commit()
            if session.modified:
                response.delete_cookie(app.session_cookie_name, domain=domain)
            return

        val = self.serializer.dumps(dict(session))
        db.session.add(FlaskSession.change(session.sid, val))
        db.session.commit()

        httponly = self.get_cookie_httponly(app)
        secure   = self.get_cookie_secure(app)
        expires  = self.get_expiration_time(app, session)

        response.set_cookie(app.session_cookie_name, session.sid, expires=expires,
                            httponly=httponly, domain=domain, secure=secure)

