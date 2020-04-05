import datetime
import hashlib
from unittest import mock

import pytest

import api
from store import Storage


def get_response(request,
                 headers=None,
                 context=None,
                 store=None
                 ):
    if store is None:
        store = Storage(1, 1000)
    if context is None:
        context = {}
    if headers is None:
        headers = {}
    return api.method_handler({"body": request, "headers": headers}, context, store)


def set_valid_auth(request):
    if request.get("login") == api.ADMIN_LOGIN:
        request["token"] = hashlib.sha512(
            (datetime.datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT).encode('UTF8')).hexdigest()
    else:
        msg = request.get("account", "") + request.get("login", "") + api.SALT
        request["token"] = hashlib.sha512(msg.encode('UTF8')).hexdigest()


def test_empty_request():
    _, code = get_response({})
    assert api.INVALID_REQUEST == code


@pytest.mark.parametrize(
    'req',
    [
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "", "arguments": {}},
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "sdd", "arguments": {}},
        {"account": "horns&hoofs", "login": "admin", "method": "online_score", "token": "", "arguments": {}},
    ]
)
def test_bad_auth(req):
    _, code = get_response(req)
    assert api.FORBIDDEN == code


@pytest.mark.parametrize(
    'req',
    [
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score"},
        {"account": "horns&hoofs", "login": "h&f", "arguments": {}},
        {"account": "horns&hoofs", "method": "online_score", "arguments": {}},
    ]
)
def test_invalid_method_request(req):
    set_valid_auth(req)
    response, code = get_response(req)
    assert api.INVALID_REQUEST == code
    assert len(response)


@pytest.mark.parametrize(
    'arguments',
    [
        {},
        {"phone": "79175002040"},
        {"phone": "89175002040", "email": "stupnikov@otus.ru"},
        {"phone": "79175002040", "email": "stupnikovotus.ru"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": -1},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": "1"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.1890"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "XXX"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": 1},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
         "first_name": "s", "last_name": 2},
        {"phone": "79175002040", "birthday": "01.01.2000", "first_name": "s"},
        {"email": "stupnikov@otus.ru", "gender": 1, "last_name": 2},
    ]
)
def test_invalid_score_request(arguments):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request)
    assert api.INVALID_REQUEST == code, arguments
    assert len(response)


@pytest.mark.parametrize(
    'arguments',
    [
        {"phone": "79175002040", "email": "stupnikov@otus.ru"},
        {"phone": 79175002040, "email": "stupnikov@otus.ru"},
        {"gender": 1, "birthday": "01.01.2000", "first_name": "a", "last_name": "b"},
        {"gender": 0, "birthday": "01.01.2000"},
        {"gender": 2, "birthday": "01.01.2000"},
        {"first_name": "a", "last_name": "b"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
         "first_name": "a", "last_name": "b"},
    ]
)
def test_ok_score_request(arguments):
    context = {}
    request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, context=context)
    assert api.OK == code, arguments
    score = float(response.get("score"))
    assert isinstance(score, (int, float)) and score >= 0, arguments
    assert sorted(context["has"]) == sorted(arguments.keys())


def test_ok_score_admin_request():
    arguments = {"phone": "79175002040", "email": "stupnikov@otus.ru"}
    request = {"account": "horns&hoofs", "login": "admin", "method": "online_score", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request)
    assert api.OK == code
    score = response.get("score")
    assert score == '42'


@pytest.mark.parametrize(
    'arguments',
    [
        {},
        {"date": "20.07.2017"},
        {"client_ids": [], "date": "20.07.2017"},
        {"client_ids": {1: 2}, "date": "20.07.2017"},
        {"client_ids": ["1", "2"], "date": "20.07.2017"},
        {"client_ids": [1, 2], "date": "XXX"},
    ]
)
def test_invalid_interests_request(arguments):
    request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request)
    assert api.INVALID_REQUEST == code, arguments
    assert len(response)


@pytest.mark.parametrize(
    'arguments',
    [
        {"client_ids": [1, 2, 3], "date": datetime.datetime.today().strftime("%d.%m.%Y")},
        {"client_ids": [1, 2], "date": "19.07.2017"},
        {"client_ids": [0]},
    ]
)
@mock.patch('api.Storage.get', return_value='{"interests": ["piano", "guitar"]}')
def test_ok_interests_request(_, arguments):
    context = {}
    request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
    set_valid_auth(request)
    response, code = get_response(request, context=context)
    assert api.OK == code, arguments
    assert len(arguments["client_ids"]) == len(response)
    assert all(v and isinstance(v, dict) and all(isinstance(i, str) for i in v['interests'])
                   for v in response.values())
    assert context.get("nclients") == len(arguments["client_ids"])
