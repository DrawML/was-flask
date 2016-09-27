import redis

redis_cache = redis.StrictRedis(host='localhost', port=6379, db=0)
redis_cache.SUCCESS = 'success'
redis_cache.FAIL    = 'fail'
redis_cache.CANCEL  = 'cancel'
redis_cache.RUNNING = 'running'


class RedisKeyMaker:
    DATA_PROCESSING = 1
    MODEL_TRAINING = 2

    @staticmethod
    def make_key(exp_id, type):
        return str(exp_id) + '-' + str(type)
