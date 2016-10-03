import json
import os
import xml.etree.ElementTree as Et
from app.mysql_models import Experiment
import app.experiment.object_code.scripts.data_process as data_process
import pickle
from app.dist_task.src.dist_system.client import Client
from app.redis import redis_cache, RedisKeyMaker
from app.mysql_models import Data, TrainedModel
from app.mysql import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app


class TaskRunner:
    def __init__(self, user_id: int, xml,
                 data_obj_code, data_input_files, data_key: str,
                 model_obj_code, model_input_file, model_key: str):
        self.user_id            = user_id
        self.xml                = xml
        self.data_obj_code      = data_obj_code
        self.data_input_files   = data_input_files
        self.data_key           = data_key,
        self.model_obj_code     = model_obj_code
        self.model_input_file   = model_input_file
        self.model_key          = model_key
        self.valid              = True
        self.entry_arguments    = None
        self.config()

    def config(self):
        check_data  = (self.data_obj_code is not None and self.data_input_files is not None)
        check_model = (self.model_obj_code is not None and self.model_input_file is not None)
        if not check_data and not check_model:
            self.valid = False
            return

        if check_model:
            # Gonna be changed to 'model_input_file'
            input_path = 'app/experiment/object_code/test/linear_regression_input.txt'

            def get_dummy_input(input_path: str):
                with open(input_path, 'r', encoding='utf-8') as f:
                    return f.read()

            tensorflow_task_job_dict = dict()
            tensorflow_task_job_dict['data_file_token'] = get_dummy_input(input_path)
            tensorflow_task_job_dict['object_code'] = self.model_obj_code

            self.entry_arguments = dict(
                experiment_id=self.model_key,
                task_type=Client.TaskType.TYPE_TENSORFLOW_TASK,
                task_job_dict=tensorflow_task_job_dict,
                callback=self.create_callback(self.model_key, self.entry_arguments)
            )

        if check_data:
            data_processing_task_job_dict = dict()
            data_processing_task_job_dict['data_file_num'] = len(self.data_input_files)
            data_processing_task_job_dict['data_file_token_list'] = self.data_input_files
            data_processing_task_job_dict['object_code'] = self.data_obj_code

            self.entry_arguments = dict(
                experiment_id=self.model_key,
                task_type=Client.TaskType.TYPE_DATA_PROCESSING_TASK,
                task_job_dict=data_processing_task_job_dict,
                callback=self.create_callback(str(self.data_key), self.entry_arguments)
            )
        return

    def create_callback(self, task_key: str, task_args: dict):
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
        if task_args is not None:
            next_arguments = task_args

        def _callback(status: str, body=None):
            print('[run_experiment] ', 'callbacked! ')

            if status == 'success':
                task_type = key.split('-')[1]
                if task_type == str(RedisKeyMaker.DATA_PROCESSING):
                    exp_id = key.split('-')[0]
                    current_time = datetime.now().isoformat()
                    file_name = exp_id + 'exp-data-' + current_time
                    file_token = body.get('result_file_token', None)
                    new_data = Data(name=file_name, user_id=self.user_id, path=file_token)
                    try:
                        db.session.add(new_data)
                        db.session.commit()
                    except SQLAlchemyError as e:
                        db.session.rollback()
                        redis_cache.set(key, redis_cache.FAIL)
                        current_app.logger.error(e)
                        return
                    # update file token
                    next_arguments['data_file_token'] = file_token
                    current_app.logger.info('data created :' + str(new_data))
                elif task_type == str(RedisKeyMaker.MODEL_TRAINING):
                    exp_id = key.split('-')[0]
                    current_time = datetime.now().isoformat()
                    file_name = exp_id + 'exp-train-' + current_time
                    file_token = body.get('session_file_token', None)
                    new_model = TrainedModel(name=file_name, user_id=self.user_id,
                                             path=file_token, xml=pickle.dumps(self.xml))
                    try:
                        db.session.add(new_model)
                        db.session.commit()
                    except SQLAlchemyError as e:
                        db.session.rollback()
                        redis_cache.set(key, redis_cache.FAIL)
                        current_app.logger.error(e)
                        return
                    current_time = datetime.now().isoformat()
                    file_name = exp_id + 'exp-train-result-' + current_time
                    file_token = body.get('result_file_token', None)
                    new_data = Data(name=file_name, user_id=self.user_id, path=file_token)
                    try:
                        db.session.add(new_data)
                        db.session.commit()
                    except SQLAlchemyError as e:
                        db.session.rollback()
                        redis_cache.set(key, redis_cache.FAIL)
                        current_app.logger.error(e)
                        return
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


class ExperimentError(Exception):
    pass


class XMLTree:
    def __init__(self, xml):
        if os.path.isfile(xml) is True:
            self.xml_tree = Et.parse(xml)
            self.xml_tree.getroot()
        else:
            self.xml_tree = Et.fromstring(xml)
        self.root = self.xml_tree
        if self.root.tag != "experiment":
            raise ExperimentError()


class DataProcessor:
    def __init__(self, xml):
        self.root = XMLTree(xml).root
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
    SCRIPT_MODULE = 'app.experiment.object_code.scripts'

    def __init__(self, xml):
        self.root = XMLTree(xml).root
        self.model_type = self.root.find("model").find("type").text

    def generate_object_code(self):
        # have to consider about exception
        script_module = __import__(self.SCRIPT_MODULE, globals(),
                                   locals(), [self.model_type], 0)
        object_script = getattr(script_module, self.model_type)
        template_name = self.root.find("model").find("type").text + "_train"
        return object_script.make_code(self.root, template_name)

    def run_obj_code(self, obj_code):
        """This function just for test object code"""
        OUTPUT_PATH = '/Users/chan/test/output.py'
        output_file = open(OUTPUT_PATH, "w")
        output_file.write(obj_code)
        output_file.close()


class Refiner(json.JSONEncoder):
    def __init__(self, exps):
        super().__init__()
        if type(exps) is not list:
            self.exps = self.exp_to_dict(exps)
        else:
            self.exps = []
            for exp in exps:
                temp = self.exp_to_dict(exp)
                self.exps.append(temp)

    def exp_to_dict(self, exp):
        exp_dict = dict(
            id=exp.id,
            date_modified=str(exp.date_modified),
            date_created=str(exp.date_created),
            user_id=exp.user_id,
            name=exp.name,
            xml=exp.xml.decode(),
            drawing=exp.drawing.decode(),
            input=exp.input
        )
        return exp_dict


class JsonParser:
    @staticmethod
    def parse_post(json, user_id):
        try:
            exp_json = json['exp_data']
            exp_data = Experiment(exp_json['name'],
                                  user_id,
                                  pickle.dumps(exp_json['xml']),
                                  pickle.dumps(exp_json['drawing']),
                                  exp_json['input'])
        except KeyError as e:
            return e
        return exp_data
