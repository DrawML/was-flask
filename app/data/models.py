import os

from app.cloud_dfs.connector import CloudDFSConnector
from app.mysql_models import Data
from app.mysql import DrawMLRepository
import json

from config.app_config import CLOUDDFS_ADDR
from config.app_config import CLOUDDFS_PORT


class Refiner(json.JSONEncoder):
    def __init__(self, data_set):
        super().__init__()
        if type(data_set) is not list:
            self.store = self.data_to_dict(data_set)
        else:
            self.store = []
            for data in data_set:
                temp = self.data_to_dict(data)
                self.store.append(temp)

    def data_to_dict(self, data):
        return dict(
            id=data.id,
            date_modified=str(data.date_modified),
            date_created=str(data.date_created),
            user_id=data.user_id,
            name=data.name,
            path=data.path,
        )

    def get(self):
        return self.store


class ChunkRange:
    def __init__(self, range_str):
        """
        :param range_str: 'bytes 0-4194303/4271616'
        """
        self.head  = int(range_str.split(' ')[1].split('-')[0])
        self.tail  = int(range_str.split(' ')[1].split('-')[1].split('/')[0])
        self.total = int(range_str.split(' ')[1].split('-')[1].split('/')[1]) - 1


class DataManager:
    def __init__(self, id: int=-1, user_id: int=-1,
                 name: str='None', path: str='None', type='input'):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.path = path
        self.type = type
        self.db = DrawMLRepository().db

    def fetch(self):
        return self.db.session.query(Data).filter(Data.id == self.id).all()

    def check(self):
        query_data = self.db.session.query(Data). \
            filter(Data.user_id == self.user_id, Data.name == self.name).all()
        return len(query_data) > 0

    def save(self, fs_path=None):
        if not fs_path:
            fs = CloudDFSConnector(CLOUDDFS_ADDR, CLOUDDFS_PORT)
            with open(self.path, 'rt') as f:
                fs_path = fs.put_data_file(self.name, f.read())
        new_data = Data(name=self.name, user_id=self.user_id, path=fs_path, type=self.type)
        self.db.session.add(new_data)
        self.db.session.commit()
        if os.path.exists(self.path):
            os.remove(self.path)
        return new_data

    def remove(self):
        fs_path = self.fetch()[0].path
        CloudDFSConnector(CLOUDDFS_ADDR, CLOUDDFS_PORT).del_data_file(fs_path)
        self.db.session.query(Data).filter(Data.id == self.id) \
            .delete(synchronize_session=False)
        self.db.session.commit()
