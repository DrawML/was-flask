from datetime import datetime

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.dist_task.src.dist_system.client import Client
from app.mysql_models import Data
from app.redis import RedisKeyMaker, redis_cache


class TaskRunner:
    def __init__(self, user_id: int,
                 model_obj_code, model_input_file, model_key: str):
        self.user_id            = user_id
        self.model_obj_code     = model_obj_code
        self.model_input_file   = model_input_file
        self.model_key          = model_key
        self.valid              = True
        self.entry_arguments    = None
        self.config()

    def config(self):
        check_model = (self.model_obj_code is not None and self.model_input_file is not None)
        if not check_model:
            self.valid = False
            return

        if check_model:
            # Gonna be changed to 'model_input_file'
            input_path = 'app/common/object_code/test/linear_regression_input.txt'

            def get_dummy_input(input_path: str):
                with open(input_path, 'r', encoding='utf-8') as f:
                    return f.read()

            tensorflow_test_task_job_dict = dict()
            tensorflow_test_task_job_dict['data_file_token'] = get_dummy_input(input_path)
            tensorflow_test_task_job_dict['session_file_token'] = None
            tensorflow_test_task_job_dict['object_code'] = self.model_obj_code
            self.entry_arguments = dict(
                experiment_id=self.model_key,
                task_type=Client().TaskType.TYPE_TENSORFLOW_TEST_TASK,
                task_job_dict=tensorflow_test_task_job_dict,
                callback=self.create_callback(self.model_key, self.entry_arguments)
            )
        return

    def create_callback(self, task_key: str, task_args: dict):
        """
        # # Callback parameter
        # <status>
        #   - ["success", "error", "cancel"]: str
        # <body>
        #   - dict      when "success",
        #       { "stdout", "stderr", "result_file_token" }
        #   - str       when "error"
        #   - None      when "cancel"
        """
        key = task_key

        def _callback(status: str, body=None):
            print('[run_experiment] ', 'callbacked! ')

            if status == 'success':
                task_type = key.split('-')[1]
                if task_type == str(RedisKeyMaker.MODEL_TESTING):
                    model_id = key.split('-')[0]
                    current_time = datetime.now().isoformat()
                    file_name = model_id + 'model-test-result-' + current_time
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
                    current_app.logger.info('data created :' + str(new_data))
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
        return _callback

    def run(self):
        if self.valid is False:
            return self.valid
        redis_cache.set(self.entry_arguments['experiment_id'], redis_cache.RUNNING)
        Client().request_task(**self.entry_arguments)
        return self.valid
