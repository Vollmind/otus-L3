import pytest

from scoring import get_interests


def test_get_interests_normal(store, redis_connection):
    redis_connection.set('i:1', '{"interests": ["piano", "guitar"]}')
    interests = get_interests(store, 1)
    assert interests == {'interests': ["piano", "guitar"]}, interests
    redis_connection.delete('i:1')


def test_get_interests_no_data(store, redis_connection):
    with pytest.raises(KeyError):
        get_interests(store, 1)
