from datetime import datetime

import pytest

from api import CharField, ArgumentsField, EmailField, PhoneField, DateField, BirthDayField, GenderField, ClientIDsField


def test_schema_charfield_normal():
    class Dummy:
        fld = CharField(nullable=True)

    dummy = Dummy()
    dummy.fld = 'qwe'
    assert dummy.fld == 'qwe'


def test_schema_arguments_normal():
    class Dummy:
        fld = ArgumentsField(nullable=True)

    dummy = Dummy()
    dummy.fld = {'q': 1}
    assert dummy.fld == {'q': 1}


def test_schema_email_normal():
    class Dummy:
        fld = EmailField(nullable=True)

    dummy = Dummy()
    dummy.fld = 'mail@mail'
    assert dummy.fld == 'mail@mail'


def test_schema_phone_normal():
    class Dummy:
        fld = PhoneField(nullable=True)

    dummy = Dummy()
    dummy.fld = '79182231111'
    assert dummy.fld == '79182231111'


def test_schema_phone_numb_normal():
    class Dummy:
        fld = PhoneField(nullable=True)

    dummy = Dummy()
    dummy.fld = 79182231111
    assert dummy.fld == '79182231111'


def test_schema_data_normal():
    class Dummy:
        fld = DateField(nullable=True)

    dummy = Dummy()
    dummy.fld = '01.01.2000'
    assert dummy.fld == datetime.strptime('01.01.2000', '%d.%m.%Y')


def test_schema_birthday_normal():
    class Dummy:
        fld = BirthDayField(nullable=True)

    dummy = Dummy()
    dummy.fld = '01.01.2000'
    assert dummy.fld == datetime.strptime('01.01.2000', '%d.%m.%Y')


def test_schema_gender_normal():
    class Dummy:
        fld = GenderField(nullable=True)

    dummy = Dummy()
    dummy.fld = 2
    assert dummy.fld == 2


def test_schema_gender_zero_normal():
    class Dummy:
        fld = GenderField(nullable=True)

    dummy = Dummy()
    dummy.fld = 0
    assert dummy.fld == 0


def test_schema_client_ids_normal():
    class Dummy:
        fld = ClientIDsField(nullable=True)

    dummy = Dummy()
    dummy.fld = [1, 2, 3, 4]
    assert dummy.fld == [1, 2, 3, 4]


def test_schema_char_errors():
    class Dummy:
        fld = CharField(nullable=False)

    dummy = Dummy()
    with pytest.raises(ValueError):
        dummy.fld = 123


def test_schema_arguments_errors():
    class Dummy:
        fld = ArgumentsField(nullable=False)

    dummy = Dummy()
    with pytest.raises(ValueError):
        dummy.fld = 'q'


def test_schema_email_errors():
    class Dummy:
        fld = EmailField(nullable=False)

    dummy = Dummy()
    with pytest.raises(ValueError):
        dummy.fld = 123


def test_schema_email_nosign_errors():
    class Dummy:
        fld = EmailField(nullable=False)

    dummy = Dummy()
    with pytest.raises(ValueError):
        dummy.fld = 'mail'


def test_schema_phone_errors():
    class Dummy:
        fld = PhoneField(nullable=False)

    dummy = Dummy()
    with pytest.raises(ValueError):
        dummy.fld = 11.22


def test_schema_phone_len_errors():
    class Dummy:
        fld = PhoneField(nullable=False)

    dummy = Dummy()
    with pytest.raises(ValueError):
        dummy.fld = 723123


def test_schema_phone_7_errors():
    class Dummy:
        fld = PhoneField(nullable=False)

    dummy = Dummy()
    with pytest.raises(ValueError):
        dummy.fld = 12312312312


def test_schema_date_errors():
    class Dummy:
        fld = DateField(nullable=False)

    dummy = Dummy()
    with pytest.raises(ValueError):
        dummy.fld = 123


def test_schema_birthday_errors():
    class Dummy:
        fld = BirthDayField(nullable=False)

    dummy = Dummy()
    with pytest.raises(ValueError):
        dummy.fld = 123


def test_schema_birthday_old_errors():
    class Dummy:
        fld = BirthDayField(nullable=False)

    dummy = Dummy()
    with pytest.raises(ValueError):
        dummy.fld = datetime.now().replace(year=datetime.now().year-71).strftime('%d.%m.%Y')


def test_schema_gender_errors():
    class Dummy:
        fld = GenderField(nullable=False)

    dummy = Dummy()
    with pytest.raises(ValueError):
        dummy.fld = 'q'


def test_schema_gender_range_errors():
    class Dummy:
        fld = GenderField(nullable=False)

    dummy = Dummy()
    with pytest.raises(ValueError):
        dummy.fld = 3


def test_schema_client_ids_errors():
    class Dummy:
        fld = ClientIDsField(nullable=False)

    dummy = Dummy()
    with pytest.raises(ValueError):
        dummy.fld = 123


def test_schema_client_ids_inner_errors():
    class Dummy:
        fld = ClientIDsField(nullable=False)

    dummy = Dummy()
    with pytest.raises(ValueError):
        dummy.fld = [1, 2, '123']
