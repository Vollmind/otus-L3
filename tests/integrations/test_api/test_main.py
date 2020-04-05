import hashlib
from datetime import datetime

import requests


def test_main(server_fixture, url):
    data = {
        "account": "horns&hoofs",
        "login": "h&f",
        "method": "online_score",
        "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
        "arguments":
            {
                "phone": "79175002040",
                "email": "stupnikov@otus.ru",
            }
    }
    resp = requests.post(url, json=data)
    assert resp.json() == {'response': {'score': '3.0'}, 'code': 200}


def test_admin(server_fixture, url):
    data = {
        "account": "horns&hoofs",
        "login": "admin",
        "method": "online_score",
        "token": hashlib.sha512((datetime.now().strftime("%Y%m%d%H") + '42').encode('UTF8')).hexdigest(),
        "arguments":
            {
                "phone": "79175002040",
                "email": "stupnikov@otus.ru",
            }
    }
    resp = requests.post(url, json=data)
    assert resp.json() == {'response': {'score': '42'}, 'code': 200}


def test_main_no_account(server_fixture, url):
    data = {
        "login": "h&f",
        "method": "online_score",
        "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
        "arguments":
            {
                "phone": "79175002040",
                "email": "stupnikov@otus.ru",
            }
    }
    resp = requests.post(url, json=data)
    assert resp.json() == {'code': 500, 'error': 'Internal Server Error'}


def test_main_no_login(server_fixture, url):
    data = {
        "account": "horns&hoofs",
        "method": "online_score",
        "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
        "arguments":
            {
                "phone": "79175002040",
                "email": "stupnikov@otus.ru",
            }
    }
    resp = requests.post(url, json=data)
    assert resp.json() == {'code': 422, 'error': 'Validation error - require field "login"'}


def test_main_no_method(server_fixture, url):
    data = {
        "account": "horns&hoofs",
        "login": "h&f",
        "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
        "arguments":
            {
                "phone": "79175002040",
                "email": "stupnikov@otus.ru",
            }
    }
    resp = requests.post(url, json=data)
    assert resp.json() == {'code': 422, 'error': 'Validation error - require field "method"'}


def test_main_no_token(server_fixture, url):
    data = {
        "account": "horns&hoofs",
        "login": "h&f",
        "method": "online_score",
        "arguments":
            {
                "phone": "79175002040",
                "email": "stupnikov@otus.ru",
            }
    }
    resp = requests.post(url, json=data)
    assert resp.json() == {'code': 422, 'error': 'Validation error - require field "token"'}


def test_main_no_arguments(server_fixture, url):
    data = {
        "account": "horns&hoofs",
        "login": "h&f",
        "method": "online_score",
        "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
    }
    resp = requests.post(url, json=data)
    assert resp.json() == {'code': 422, 'error': 'Validation error - require field "arguments"'}


def test_main_auth_error(server_fixture, url):
    data = {
        "account": "horns&hoofs",
        "login": "h&f",
        "method": "online_score",
        "token": "1",
        "arguments":
            {
                "phone": "79175002040",
                "email": "stupnikov@otus.ru",
            }
    }
    resp = requests.post(url, json=data)
    assert resp.json() == {'code': 403, 'error': 'Forbidden'}


def test_main_wrong_method(server_fixture, url):
    data = {
        "account": "horns&hoofs",
        "login": "h&f",
        "method": "dunno",
        "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
        "arguments":
            {
                "phone": "79175002040",
                "email": "stupnikov@otus.ru",
            }
    }
    resp = requests.post(url, json=data)
    assert resp.json() == {'code': 404, 'error': 'Not Found'}
