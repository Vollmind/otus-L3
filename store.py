import logging
from datetime import timedelta

import redis

TRY_COUNT = 5


def some_tries(throw_last_exception):
    def tries(func):
        tle = throw_last_exception

        def wrapper(*args, **kwargs):
            result = None
            last_ex = None
            for i in range(1 if not TRY_COUNT else TRY_COUNT):
                try:
                    result = func(*args, **kwargs)
                    last_ex = None
                    break
                except Exception as e:
                    logging.exception(e)
                    last_ex = e
            if tle and last_ex:
                raise last_ex
            return result

        return wrapper
    return tries


class Storage:
    _redis = None

    def __init__(self, db, timeout):
        self._redis = redis.Redis(db=db, socket_timeout=timeout, socket_keepalive=True)

    @some_tries(throw_last_exception=True)
    def get(self, key):
        res = self._redis.get(key)
        if res:
            return res.decode('UTF8')
        else:
            raise KeyError('No key in redis')

    @some_tries(throw_last_exception=False)
    def cache_set(self, key, value, time):
        self._redis.setex(key, timedelta(seconds=time), value=value)

    @some_tries(throw_last_exception=False)
    def cache_get(self, key):
        return self._redis.get(key).decode('UTF8')
