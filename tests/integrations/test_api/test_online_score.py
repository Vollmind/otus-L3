import pytest
import requests


@pytest.fixture
def base_data():
    return {
        "account": "horns&hoofs",
        "login": "h&f",
        "method": "online_score",
        "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
    }


def test_correct(server_fixture, url, base_data):
    base_data['arguments'] = {
        "phone": "79175002040",
        "email": "stupnikov@otus.ru",
        "first_name": "Стансилав",
        "last_name": "Ступников",
        "birthday": "01.01.1990",
        "gender": 1
    }
    resp = requests.post(url, json=base_data)
    assert resp.json() == {'response': {'score': '5.0'}, 'code': 200}


def test_correct_names(server_fixture, url, base_data):
    base_data['arguments'] = {
        "first_name": "Стансилав",
        "last_name": "Ступников",
    }
    resp = requests.post(url, json=base_data)
    assert resp.json() == {'response': {'score': '0.5'}, 'code': 200}


def test_wrong_fname(server_fixture, url, base_data):
    base_data['arguments'] = {
        "first_name": 1,
        "last_name": "Ступников",
    }
    resp = requests.post(url, json=base_data)
    assert resp.json() == {'code': 422, 'error': 'Wrong type for field "first_name"'}


def test_wrong_lname(server_fixture, url, base_data):
    base_data['arguments'] = {
        "first_name": "Стансилав",
        "last_name": 1,
    }
    resp = requests.post(url, json=base_data)
    assert resp.json() == {'code': 422, 'error': 'Wrong type for field "last_name"'}


def test_correct_bd_gnd(server_fixture, url, base_data):
    base_data['arguments'] = {
        "birthday": "01.01.1990",
        "gender": 1
    }
    resp = requests.post(url, json=base_data)
    assert resp.json() == {'response': {'score': '1.5'}, 'code': 200}


def test_wrong_bd(server_fixture, url, base_data):
    base_data['arguments'] = {
        "birthday": "01.01.1890",
        "gender": 1
    }
    resp = requests.post(url, json=base_data)
    assert resp.json() == {'code': 422, 'error': 'Day of birth must be within 70 years'}


def test_wrong_gnd(server_fixture, url, base_data):
    base_data['arguments'] = {
        "birthday": "01.01.1990",
        "gender": 7
    }
    resp = requests.post(url, json=base_data)
    assert resp.json() == {'code': 422, 'error': 'Gender must be in range(0, 2)'}


def test_correct_phone_mail(server_fixture, url, base_data):
    base_data['arguments'] = {
        "phone": "79175002040",
        "email": "stupnikov@otus.ru"
    }
    resp = requests.post(url, json=base_data)
    assert resp.json() == {'response': {'score': '3.0'}, 'code': 200}


def test_wrong_phone(server_fixture, url, base_data):
    base_data['arguments'] = {
        "phone": "0",
        "email": "stupnikov@otus.ru"
    }
    resp = requests.post(url, json=base_data)
    assert resp.json() == {'code': 422, 'error': 'Phone must be 11 digits'}


def test_wrong_mail(server_fixture, url, base_data):
    base_data['arguments'] = {
        "phone": "79175002040",
        "email": "stupnikovotus.ru"
    }
    resp = requests.post(url, json=base_data)
    assert resp.json() == {'code': 422, 'error': 'Email must have a "@"'}


def test_error_no_pair(server_fixture, url, base_data):
    base_data['arguments'] = {
        "email": "stupnikov@otus.ru",
        "last_name": "Ступников",
        "gender": 1
    }
    resp = requests.post(url, json=base_data)
    assert resp.json() == {'code': 422, 'error': 'No required pair'}
