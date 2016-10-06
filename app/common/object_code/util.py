import os
from datetime import datetime
from enum import Enum
from xml.etree import ElementTree as Et

import pickle
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.common.object_code.scripts import data_process as data_process
from app.dist_task.src.dist_system.client import Client
from app.mysql_models import Data, TrainedModel
from app.redis import RedisKeyMaker, redis_cache


class ExperimentError(Exception):
    pass


class TestError(Exception):
    pass


class GeneratorType(Enum):
    DATA_PROCESSING = {"GENERATOR": "data_processing", "TAG": "experiment"}
    TRAIN = {"GENERATOR": "train", "TAG": "experiment"}
    TEST = {"GENERATOR": "test", "TAG": "test"}

    def __str__(self):
        return self.value["GENERATOR"]

    def get_tag_name(self):
        return self.value["TAG"]


class XMLTree:
    TYPE = GeneratorType

    def __init__(self, xml, xml_tree_type: GeneratorType):
        self.xml_tree_type = xml_tree_type

        if os.path.isfile(xml) is True:
            self.xml_tree = Et.parse(xml)
            self.xml_tree.getroot()
        else:
            self.xml_tree = Et.fromstring(xml)
        self.root = self.xml_tree
        if self.root.tag != self.xml_tree_type.get_tag_name():
            error = self.get_error()
            raise error()

    def get_error(self):
        if self.xml_tree_type == GeneratorType.TRAIN or self.xml_tree_type == GeneratorType.DATA_PROCESSING:
            return ExperimentError
        elif self.xml_tree_type == GeneratorType.TEST:
            return TestError


class DataProcessor:
    def __init__(self, xml):
        self.root = XMLTree(xml, GeneratorType.DATA_PROCESSING).root
        self.processing = self.root.find('data_processing')

    def generate_object_code(self):
        # have to consider about exception
        return data_process.make_code(self.root)

    def run_obj_code(self, obj_code):
        """This function just for test object code"""
        OUTPUT_PATH = '/Users/chan/test/output_data.py'
        output_file = open(OUTPUT_PATH, "w")
        output_file.write(obj_code)
        output_file.close()


class TFConverter:
    """This code is NOT considered about exception"""
    SCRIPT_MODULE = 'app.common.object_code.scripts'
    TYPE = GeneratorType

    def __init__(self, xml, converter_type: GeneratorType):
        self.root = XMLTree(xml, converter_type).root
        self.model_type = self.root.find("model").find("type").text
        self.converter_type = converter_type

    def generate_object_code(self):
        # have to consider about exception
        script_module = __import__(self.SCRIPT_MODULE, globals(),
                                   locals(), [self.model_type], 0)
        object_script = getattr(script_module, self.model_type)
        template_name = self.root.find("model").find("type").text + "_{0}".format(self.converter_type)
        return object_script.make_code(self.root, template_name)

    # have to be deprecated
    def run_obj_code(self, obj_code):
        """This function just for test object code"""
        OUTPUT_PATH = '/Users/chan/test/output{0}.py'.format(self.converter_type)
        output_file = open(OUTPUT_PATH, "w")
        output_file.write(obj_code)
        output_file.close()


class TaskRunner:
    def __init__(self, user_id: int,
                 test_obj_code=None, test_input_file=None, test_key: str=None,
                 train_obj_code=None, train_input_file=None, train_key: str=None,
                 data_obj_code=None, data_input_files=None, data_key: str=None, xml=None):
        self.user_id            = user_id
        self.xml                = xml
        self.data_obj_code      = data_obj_code
        self.data_input_files   = data_input_files
        self.data_key           = data_key
        self.train_obj_code     = train_obj_code
        self.train_input_file   = train_input_file
        self.train_key          = train_key
        self.test_obj_code      = test_obj_code
        self.test_input_file   = test_input_file
        self.test_key          = test_key
        self.valid              = True
        self.entry_arguments    = None
        self.config()

    def config(self):
        check_data  = (self.data_obj_code is not None and self.data_input_files is not None)
        check_train = (self.train_obj_code is not None and self.train_input_file is not None)
        check_test  = (self.test_obj_code is not None and self.test_input_file is not None)

        if not check_data and not check_train:
            self.valid = False
            return

        if check_train:
            # Gonna be changed to 'train_input_file'
            input_path = 'app/common/object_code/test/linear_regression_input.txt'

            def get_dummy_input(input_path: str):
                with open(input_path, 'r', encoding='utf-8') as f:
                    return f.read()

            tensorflow_train_task_job_dict = dict()
            tensorflow_train_task_job_dict['data_file_token'] = get_dummy_input(input_path)
            tensorflow_train_task_job_dict['object_code'] = self.train_obj_code

            self.entry_arguments = dict(
                experiment_id=self.train_key,
                task_type=Client.TaskType.TYPE_TENSORFLOW_TRAIN_TASK,
                task_job_dict=tensorflow_train_task_job_dict,
                callback=self.create_callback(self.train_key)
            )

        if check_data:
            data_processing_task_job_dict = dict()
            data_processing_task_job_dict['data_file_num'] = len(self.data_input_files)
            data_processing_task_job_dict['data_file_token_list'] = self.data_input_files
            data_processing_task_job_dict['object_code'] = self.data_obj_code

            self.entry_arguments = dict(
                experiment_id=self.data_key,
                task_type=Client.TaskType.TYPE_DATA_PROCESSING_TASK,
                task_job_dict=data_processing_task_job_dict,
                callback=self.create_callback(self.data_key)
            )

        if check_test:
            # Gonna be changed to 'model_input_file'
            input_path = 'app/common/object_code/test/linear_regression_input.txt'

            def get_dummy_input(input_path: str):
                with open(input_path, 'r', encoding='utf-8') as f:
                    return f.read()

            tensorflow_test_task_job_dict = dict()
            tensorflow_test_task_job_dict['data_file_token'] = get_dummy_input(input_path)
            # tensorflow_test_task_job_dict['session_file_token'] = None
            tensorflow_test_task_job_dict['object_code'] = self.test_obj_code
            self.entry_arguments = dict(
                experiment_id=self.test_key,
                task_type=Client().TaskType.TYPE_TENSORFLOW_TEST_TASK,
                task_job_dict=tensorflow_test_task_job_dict,
                callback=self.create_callback(self.test_key)
            )
        return

    def create_callback(self, task_key: str):
        """
        # # Callback parameter
        # <status>
        #   - ["success", "error", "cancel"]: str
        # <body>
        #   - dict      when "success",
        #       { "stdout", "stderr", "result_file_token", "session_file_token" }
        #   - str       when "error"
        #   - None      when "cancel"
        """
        key = task_key
        if self.entry_arguments is not None:
            next_arguments = self.entry_arguments

        def _callback(status: str, body=None):
            print('[run_experiment] ', 'callbacked! ')

            def save_obj(data_class, params):
                new_one = data_class(**params)
                db.session.add(new_one)
                db.session.commit()
                return new_one

            def fail(token=None):
                if file_token:
                    from app.cloud_dfs.connector import CloudDFSConnector
                    from config.app_config import CLOUDDFS_ADDR, CLOUDDFS_PORT
                    CloudDFSConnector(CLOUDDFS_ADDR, CLOUDDFS_PORT)\
                        .del_data_file(token)
                db.session.rollback()
                redis_cache.set(key, redis_cache.FAIL)
                current_app.logger.error(e)
                return

            if status == 'success':
                task_type = key.split('-')[1]
                id = key.split('-')[0]
                current_time = datetime.now().isoformat()

                if task_type == str(RedisKeyMaker.DATA_PROCESSING):
                    file_name = '{}-data-result-{}'.format(id, current_time)
                    file_token = body.get('result_file_token', None)
                    try:
                        save_obj(Data, dict(name=file_name, user_id=self.user_id,
                                            path=file_token))
                    except SQLAlchemyError as e:
                        fail(file_token)
                    # update file token
                    next_arguments['data_file_token'] = file_token
                elif task_type == str(RedisKeyMaker.MODEL_TRAINING):
                    file_name = '{}-train-session-{}'.format(id, current_time)
                    file_token = body.get('session_file_token', None)
                    try:
                        save_obj(TrainedModel, dict(name=file_name, user_id=self.user_id,
                                                    path=file_token, xml=pickle.dumps(self.xml)))
                    except SQLAlchemyError as e:
                        fail()

                    current_time = datetime.now().isoformat()
                    file_name = '{}-train-result-{}'.format(id, current_time)
                    file_token = body.get('result_file_token', None)
                    try:
                        save_obj(Data, dict(name=file_name, user_id=self.user_id,
                                            path=file_token))
                    except SQLAlchemyError as e:
                        fail(file_token)

                if task_type == str(RedisKeyMaker.MODEL_TESTING):
                    file_name = '{}-test-result-{}'.format(id, current_time)
                    file_token = body.get('result_file_token', None)
                    try:
                        save_obj(Data, dict(name=file_name, user_id=self.user_id,
                                            path=file_token))
                    except SQLAlchemyError as e:
                        fail(file_token)
                    # update file token ??
                current_app.logger.info('Test finish: {}'.format(id))
                redis_cache.set(key, redis_cache.SUCCESS)
                print("[%d] callback is called with 'success'" % key)
            elif status == 'error':
                redis_cache.set(key, redis_cache.FAIL)
                print("[%d] callback is called with 'fail'" % key)
            elif status == 'cancel':
                # Client().request_cancel(key)
                redis_cache.set(key, redis_cache.CANCEL)
                print("[%d] callback is called with 'cancel'" % key)

            if body is not None:
                print(body['stderr'])

            if next_arguments:
                redis_cache.set(next_arguments['experiment_id'], redis_cache.RUNNING)
                Client().request_task(**next_arguments)

        return _callback

    def run(self):
        if self.valid is False:
            return self.valid
        redis_cache.set(self.entry_arguments['experiment_id'], redis_cache.RUNNING)
        Client().request_task(**self.entry_arguments)
        return self.valid
