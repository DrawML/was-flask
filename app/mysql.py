from app.common.library import SingletonType
from flask_sqlalchemy import SQLAlchemy


class DrawMLRepository(metaclass=SingletonType):
    def __init__(self, app):
        self._db = SQLAlchemy(app)

    @property
    def db(self):
        return self._db
