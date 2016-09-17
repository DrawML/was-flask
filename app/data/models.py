from app.db_models import Data
from app.database import db


class DataChecker:
    def __init__(self, filename, user_id):
        self.name = filename
        self.user_id = user_id

    def exist(self):
        query_data = db.session.query(Data). \
            filter(Data.user_id == self.user_id, Data.name == self.name).all()
        if len(query_data) > 0:
            return True
        return False
