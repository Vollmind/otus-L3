from unittest import mock
from unittest.mock import Mock

import pytest
import requests


@pytest.fixture
def base_data():
    return {
        "account": "horns&hoofs",
        "login": "h&f",
        "method": "clients_interests",
        "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
    }


def test_correct(server_fixture, url, base_data):
    base_data['arguments'] = {
        "date": '01.01.2000',
        "client_ids": [1]
    }
    resp = requests.post(url, json=base_data)
    assert resp.json() == {'code': 200, 'response': {'1': []}}


def test_no_date(server_fixture, url, base_data):
    base_data['arguments'] = {
        "client_ids": [1]
    }
    resp = requests.post(url, json=base_data)
    assert resp.json() == {'code': 200, 'response': {'1': []}}


def test_no_ids(server_fixture, url, base_data):
    base_data['arguments'] = {
        "date": '01.01.2000',
    }
    resp = requests.post(url, json=base_data)
    assert resp.json() == {'code': 422, 'error': 'Validation error - require field "client_ids"'}


def test_empty_ids(server_fixture, url, base_data):
    base_data['arguments'] = {
        "client_ids": []
    }
    resp = requests.post(url, json=base_data)
    assert resp.json() == {'code': 422, 'error': 'Trying to set None to not-nullable field "client_ids"'}


def test_correct_with_data(server_fixture, url, base_data):
    base_data['arguments'] = {
        "date": '01.01.2000',
        "client_ids": [2]
    }
    resp = requests.post(url, json=base_data)
    assert resp.json() == {'code': 200, 'response': {'2': {'interests': ['piano', 'guitar']}}}


def test_correct_id_list(server_fixture, url, base_data):
    base_data['arguments'] = {
        "date": '01.01.2000',
        "client_ids": [1, 2]
    }
    resp = requests.post(url, json=base_data)
    assert resp.json() == {'code': 200, 'response': {'1': [], '2': {'interests': ['piano', 'guitar']}}}