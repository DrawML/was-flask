from uuid import uuid4
from datetime import datetime, timedelta
from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict
import redis
import pickle


class RedisSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None, new=False):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False


class RedisSessionInterface(SessionInterface):
    def __init__(self, host='127.0.0.1', port=6379, db=0, timeout=3600):
        self.store = redis.StrictRedis(host=host, port=port, db=db)
        self.timeout = timeout

    def generate_sid(self):
        return str(uuid4())

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if sid:
            stored_session = None
            value = self.store.get(sid)
            if value:
                stored_session = pickle.loads(value)
            if stored_session:
                if stored_session.get('expiration_time') > datetime.utcnow():
                    return RedisSession(initial=stored_session['data'],
                                        sid=stored_session['sid'])
        return RedisSession(sid=self.generate_sid(), new=True)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if not session:
            response.delete_cookie(app.session_cookie_name, domain=domain)
            return

        if self.get_expiration_time(app, session):
            expiration_time = self.get_expiration_time(app, session)
        else:
            expiration_time = datetime.utcnow() + timedelta(hours=1)

        session_data = {
            'sid': session.sid,
            'data': session,
            'expication_time': expiration_time
        }
        value = pickle.dumps(session_data)
        self.store.setex(session.sid, self.timeout, value)

        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=self.get_expiration_time(app, session),
                            httponly=True, domain=domain)
