import redis

redis_cache = redis.StrictRedis(host='localhost', port=6379, db=0)


class RedisKeyMaker:
    DATA_PROCESSING = 1
    MODEL_TRAINING = 2

    @staticmethod
    def make_key(exp_id, type):
        return str(exp_id) + '-' + str(type)
