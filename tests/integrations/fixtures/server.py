import logging
import multiprocessing
import time
from http.server import HTTPServer
from unittest import mock

import pytest

from api import MainHTTPHandler


def start_server():
    logging.basicConfig(filename=None, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", 8080), MainHTTPHandler)
    server.serve_forever()


def mock_get(self, x):
    if x == 'i:1':
        return None
    else:
        return '{"interests": ["piano", "guitar"]}'


@pytest.fixture("module")
def server_fixture():
    process = multiprocessing.Process(target=start_server)
    print("Starting server")
    with mock.patch("api.Storage.get", new=mock_get):
        process.start()
        # Wait for server to start
        time.sleep(0.1)
        yield
    print("Stopping server")
    process.terminate()


@pytest.fixture()
def url():
    return 'http://127.0.0.1:8080/method/'
