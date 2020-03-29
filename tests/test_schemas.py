from datetime import datetime

import pytest

from api import CharField, ArgumentsField, EmailField, PhoneField, DateField, BirthDayField, GenderField, ClientIDsField


@pytest.mark.parametrize(
    "field,value,result",
    [
        (CharField, 'qwe', None),
        (ArgumentsField, {'q': 1}, None),
        (EmailField, 'mail@mail', None),
        (PhoneField, '79182231111', None),
        (PhoneField, 79182231111, '79182231111'),
        (DateField, '01.01.2000', datetime.strptime('01.01.2000', '%d.%m.%Y')),
        (BirthDayField, '01.01.2000', datetime.strptime('01.01.2000', '%d.%m.%Y')),
        (GenderField, 0, None),
        (GenderField, 2, None),
        (ClientIDsField, [1, 2, 3, 4], None)
    ],
    ids=[
        'CharField correct',
        'ArgumentsField correct',
        'EmailField correct',
        'PhoneField correct str',
        'PhoneField correct int',
        'DateField correct',
        'BirthDayField correct',
        'GenderField correct zero',
        'GenderField correct',
        'ClientIDsField correct',
    ]
)
def test_schema_normal(field, value, result):
    class Dummy:
        fld = field(nullable=True)

    dummy = Dummy()
    dummy.fld = value
    assert dummy.fld == (result if result else value)


@pytest.mark.parametrize(
    "field,value",
    [
        (CharField, 123),
        (ArgumentsField, 'q'),
        (EmailField, 123),
        (EmailField, 'mail'),
        (PhoneField, 33.21),
        (PhoneField, 79182),
        (PhoneField, 11111111111),
        (DateField, 11),
        (BirthDayField, 11),
        (BirthDayField, datetime.now().replace(year=datetime.now().year-71).strftime('%d.%m.%Y')),
        (GenderField, 'q'),
        (GenderField, 3),
        (ClientIDsField, 10),
        (ClientIDsField, [1, 2, '12'])
    ],
    ids=[
        'CharField wrong type',
        'ArgumentsField wrong type',
        'EmailField wrong type',
        'EmailField no @',
        'PhoneField wrong type ',
        'PhoneField no 11 len',
        'PhoneField leading 7',
        'DateField wrong type',
        'BirthDayField wrong type',
        'BirthDayField more than 70 years',
        'GenderField wrong type',
        'GenderField out of range',
        'ClientIDsField wrong type',
        'ClientIDsField wrong inner type',
    ]
)
def test_schema_value_errors(field, value):
    class Dummy:
        fld = field(nullable=False)

    dummy = Dummy()
    with pytest.raises(ValueError):
        dummy.fld = value
