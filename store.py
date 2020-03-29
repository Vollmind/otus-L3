import logging
from datetime import timedelta

import redis

TRY_COUNT = 5


def some_tries(func):
    def wrapper(*args, **kwargs):
        result = None
        for i in range(1 if not TRY_COUNT else TRY_COUNT):
            try:
                result = func(*args, **kwargs)
                break
            except Exception as e:
                logging.exception(e)
        return result

    return wrapper


class Storage:
    _redis = None

    def __init__(self, db, timeout):
        self._redis = redis.Redis(db=db, socket_timeout=timeout, socket_keepalive=True)

    @some_tries
    def get(self, key):
        return self._redis.get(key).decode('UTF8')

    @some_tries
    def cache_set(self, key, value, time):
        self._redis.setex(key, timedelta(seconds=time), value=value)

    @some_tries
    def cache_get(self, key):
        return self._redis.get(key).decode('UTF8')
