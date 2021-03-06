#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import hashlib
import json
import logging
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from optparse import OptionParser

from scoring import get_score, get_interests

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


class Field:
    field_type = None

    def __init__(self,
                 required: bool = False,
                 nullable: bool = False):
        self.required = required
        self.nullable = nullable
        self._value = None

    def value_processing(self, value):
        return value

    def validate(self, value):
        if not self.nullable and not value:
            raise ValueError(f'Trying to set None to not-nullable field "{self.name}"')
        if self.field_type is not None and not isinstance(value, self.field_type):
            raise ValueError(f'Wrong type for field "{self.name}"')

    def __get__(self, obj, cls):
        if obj is None:
            return self
        return obj.__dict__.get(self.name)

    def __set__(self, obj, value):
        value = self.value_processing(value)
        self.validate(value)
        obj.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


class CharField(Field):
    field_type = str


class ArgumentsField(Field):
    field_type = dict


class EmailField(CharField):
    def validate(self, value):
        super().validate(value)
        if '@' not in value:
            raise ValueError('Email must have a "@"')


class PhoneField(CharField):
    def value_processing(self, value):
        return str(value) if isinstance(value, int) else value

    def validate(self, value):
        super().validate(value)
        if len(value) != 11:
            raise ValueError('Phone must be 11 digits')
        if value[0] != '7':
            raise ValueError('Phone must have leading "7"')


class DateField(Field):
    def value_processing(self, value):
        return datetime.datetime.strptime(value, '%d.%m.%Y')

    field_type = datetime.datetime


class BirthDayField(DateField):

    def validate(self, value):
        super().validate(value)
        min_date = datetime.datetime.now()
        min_date = min_date.replace(year=min_date.year - 70)
        if min_date > value:
            raise ValueError('Day of birth must be within 70 years')


class GenderField(Field):
    field_type = int

    def validate(self, value):
        super().validate(value)
        if value not in range(len(GENDERS)):
            raise ValueError(f'Gender must be in {range(len(GENDERS))}')


class ClientIDsField(Field):
    field_type = list

    def validate(self, value):
        super().validate(value)
        for i in value:
            if not isinstance(i, int):
                raise ValueError('All elements must be integers!')


class BaseRequest:
    context = {}

    def validate(self, data_dict):
        logging.info(data_dict)
        fields = [(key, getattr(self.__class__, key)) for key in self.__class__.__dict__]
        for key, field in fields:
            if isinstance(field, Field) and field.required and key not in data_dict.keys():
                raise ValueError(f'Validation error - require field "{key}"')

    def load(self, data_dict):
        for key in data_dict:
            setattr(self, key, data_dict[key])

    @classmethod
    def from_dict(cls, data_dict):
        self = cls()
        self.validate(data_dict)
        self.load(data_dict)
        return self


class ClientsInterestsRequest(BaseRequest):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)

    def load(self, data_dict):
        super().load(data_dict)
        self.context = {'nclients': len(self.client_ids)}


class OnlineScoreRequest(BaseRequest):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def validate(self, data_dict):
        required_field = [
            ['first_name', 'last_name'],
            ['email', 'phone'],
            ['birthday', 'gender']
        ]
        self.context = {'has': [key for key in data_dict if data_dict[key] is not None]}
        check_result = False
        for required_field_list in required_field:
            if any([key not in data_dict or data_dict[key] is None for key in required_field_list]):
                continue
            check_result = True
            break
        if not check_result:
            raise ValueError('No required pair')

        super().validate(data_dict)


class MethodRequest(BaseRequest):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def check_auth(request):
    hash_str = None
    if request.is_admin:
        hash_str = datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT
    else:
        hash_str = request.account + request.login + SALT
    digest = hashlib.sha512(hash_str.encode('UTF8')).hexdigest()
    if digest == request.token:
        return True
    return False


def online_score_handler(store, arguments, is_admin):
    inner = OnlineScoreRequest().from_dict(arguments)
    if is_admin:
        response = {'score': 42}
    else:
        response = {
            'score': get_score(
                store,
                inner.phone,
                inner.email,
                inner.birthday,
                inner.gender,
                inner.first_name,
                inner.last_name
            )
        }
    return response, inner.context


def clients_interests_handler(store, arguments):
    inner = ClientsInterestsRequest().from_dict(arguments)
    response = {key: get_interests(store, key) for key in inner.client_ids}
    return response, inner.context


def method_handler(request, ctx, store):
    response, code, context = None, None, None
    try:
        method_request = MethodRequest().from_dict(request['body'])
        if not check_auth(method_request):
            code = FORBIDDEN
        else:
            if method_request.method == 'online_score':
                response, context = online_score_handler(
                    store,
                    method_request.arguments,
                    method_request.is_admin
                )
                code = OK
            elif method_request.method == 'clients_interests':
                response, context = clients_interests_handler(
                    store,
                    method_request.arguments
                )
                code = OK
            else:
                code = NOT_FOUND
    except ValueError as e:
        response, code = str(e), INVALID_REQUEST
    except Exception as e:
        logging.exception(e)

    if context:
        ctx.update(context)

    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode('UTF8'))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
