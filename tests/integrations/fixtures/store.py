import pytest
import redis

from store import Storage


@pytest.fixture
def store():
    return Storage(1, 1000)


@pytest.fixture
def redis_connection():
    return redis.Redis(db=1, socket_timeout=1000)


@pytest.fixture
def store_base_data(redis_connection):
    redis_connection.set('1', '2')
    yield
    redis_connection.delete('1')
