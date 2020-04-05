import hashlib

from scoring import get_score


def test_get_score_check_cache(store, redis_connection):
    phone = '79189181122'
    mail = 'test@mail'
    storekey = "uid:" + hashlib.md5(phone.encode('UTF8')).hexdigest()
    redis_connection.delete(storekey)
    score = get_score(store, phone, mail)
    assert score == '3.0'
    assert redis_connection.get(storekey).decode('UTF8') == '3.0'


def test_get_score_two_times(store, redis_connection):
    phone = '79189181122'
    mail = 'test@mail'
    storekey = "uid:" + hashlib.md5(phone.encode('UTF8')).hexdigest()
    redis_connection.delete(storekey)
    score = get_score(store, phone, mail)
    assert score == '3.0'
    assert redis_connection.get(storekey).decode('UTF8') == '3.0'
    score = get_score(store, phone, None)
    assert score == '3.0'
    redis_connection.delete(storekey)
    assert redis_connection.get(storekey) is None
    score = get_score(store, phone, None)
    assert score == '1.5'

