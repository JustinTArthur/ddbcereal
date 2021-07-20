from decimal import Decimal
from fractions import Fraction

import pytest

from ddbcereal.deserializing import Deserializer, PythonNumber

NUM_SMALL_INT = {'N': '42'}
NUM_SMALL_NEG_INT = {'N': '-42'}
NUM_NTSC_FILM_APPROX = {'N': '23.976023976023976023976023976023976024'}
NUM_SHORT_DECIMAL = {'N': '1.1'}
NUM_WIDER_THAN_SHORT_FLOAT_REPR = {'N': '1.10000000000000008881784197001252323'
                                        '39'}
NUM_TRICKY_PRECISION = {'N': '100000000000000000000000000000000000000000000000'
                             '000000000000000000000000000000000000000000000000'
                             '00000'}


def test_basic_types():
    deserializer = Deserializer()
    assert deserializer.deserialize({'NULL': True}) is None
    assert deserializer.deserialize({'S': 'Hello'}) == 'Hello'
    assert deserializer.deserialize({'BOOL': True}) is True
    assert deserializer.deserialize({'BOOL': False}) is False
    assert deserializer.deserialize(
        {'L': [{'NULL': True}, {'S': 'Hello'}]}
    ) == [None, 'Hello']


def test_binary():
    deserializer = Deserializer()
    raw_deserializer = Deserializer(raw_transport=True)
    assert deserializer.deserialize({'B': b''}) == b''
    assert raw_deserializer.deserialize({'B': ''}) == b''

    assert deserializer.deserialize({'B': b'test'}) == b'test'
    assert raw_deserializer.deserialize({'B': 'dGVzdA=='})


def test_item():
    deserializer = Deserializer()
    assert deserializer.deserialize_item(
        {
            'key1': {'NULL': True},
            'key2': {'S': 'Hello'}
        }
    ) == {'key1': None, 'key2': 'Hello'}


def test_map():
    deserializer = Deserializer()
    assert deserializer.deserialize(
        {
            'M': {
                'key1': {'NULL': True},
                'key2': {'S': 'Hello'}
            }
        }
    ) == {'key1': None, 'key2': 'Hello'}

    assert deserializer.deserialize(
        {
            'M': {
                'key1': {'NULL': True},
                'key2': {'S': 'Hello'},
                'key3': {
                    'M': {
                        'key3_1': {'BOOL': False},
                        'key3_2': {'L': [{'NULL': True}, {'S': 'Hello'}]}
                    }
                }
            }
        }
    ) == {
        'key1': None,
        'key2': 'Hello',
        'key3': {
            'key3_1': False,
            'key3_2': [None, 'Hello']
        }
    }


def test_decimal_only():
    deserializer = Deserializer(number_type=PythonNumber.DECIMAL_ONLY)
    assert deserializer.deserialize(NUM_SMALL_INT) == Decimal('42')
    assert deserializer.deserialize(NUM_SMALL_NEG_INT) == Decimal('-42')
    assert deserializer.deserialize(NUM_SHORT_DECIMAL) == Decimal('1.1')
    assert (deserializer.deserialize(NUM_NTSC_FILM_APPROX)
            == Decimal('23.976023976023976023976023976023976024'))
    assert (deserializer.deserialize(NUM_WIDER_THAN_SHORT_FLOAT_REPR)
            == Decimal('1.1000000000000000888178419700125232339'))
    assert (deserializer.deserialize(NUM_TRICKY_PRECISION) ==
            Decimal('1E+100'))


def test_float_only():
    deserializer = Deserializer(
        allow_inexact=True,
        number_type=PythonNumber.FLOAT_ONLY,
    )
    assert deserializer.deserialize(NUM_SMALL_INT) == 42.0
    assert deserializer.deserialize(NUM_SMALL_NEG_INT) == -42.0
    assert (deserializer.deserialize(NUM_NTSC_FILM_APPROX)
            == 23.976023976023978)
    assert (deserializer.deserialize(NUM_WIDER_THAN_SHORT_FLOAT_REPR)
            == 1.1)
    assert (deserializer.deserialize(NUM_TRICKY_PRECISION) == 1e+100)


def test_fraction_only():
    deserializer = Deserializer(
        number_type=PythonNumber.FRACTION_ONLY
    )
    assert deserializer.deserialize(NUM_SMALL_INT) == Fraction('42')
    assert deserializer.deserialize(NUM_SMALL_NEG_INT) == Fraction('-42')
    assert (deserializer.deserialize(NUM_NTSC_FILM_APPROX)
            == Fraction('23.976023976023976023976023976023976024'))
    assert (deserializer.deserialize(NUM_WIDER_THAN_SHORT_FLOAT_REPR)
            == Fraction('1.1000000000000000888178419700125232339'))
    assert (deserializer.deserialize(NUM_TRICKY_PRECISION)
            == Fraction('1e+100'))


def test_int_only():
    exact = Deserializer(number_type=PythonNumber.INT_ONLY,
                         allow_inexact=False)
    inexact = Deserializer(number_type=PythonNumber.INT_ONLY,
                           allow_inexact=True)

    assert exact.deserialize(NUM_SMALL_INT) == 42
    assert inexact.deserialize(NUM_SMALL_INT) == 42

    assert exact.deserialize(NUM_SMALL_NEG_INT) == -42
    assert inexact.deserialize(NUM_SMALL_NEG_INT) == -42

    with pytest.raises(ValueError):
        assert exact.deserialize(NUM_NTSC_FILM_APPROX) == 23
    assert inexact.deserialize(NUM_NTSC_FILM_APPROX) == 24

    with pytest.raises(ValueError):
        assert exact.deserialize(NUM_WIDER_THAN_SHORT_FLOAT_REPR) == 1
    assert inexact.deserialize(NUM_WIDER_THAN_SHORT_FLOAT_REPR) == 1

    assert (exact.deserialize(NUM_TRICKY_PRECISION)
            == 0x1249ad2594c37ceb0b2784c4ce0bf38ace408e211a7caab24308a82e8f10000000000000000000000000)
    assert (inexact.deserialize(NUM_TRICKY_PRECISION)
            == 0x1249ad2594c37ceb0b2784c4ce0bf38ace408e211a7caab24308a82e8f10000000000000000000000000)


def test_int_or_decimal():
    deserializer = Deserializer(number_type=PythonNumber.INT_OR_DECIMAL)
    small_int = deserializer.deserialize(NUM_SMALL_INT)
    assert small_int == 42
    assert isinstance(small_int, int)
    small_neg_int = deserializer.deserialize(NUM_SMALL_NEG_INT)
    assert small_neg_int == -42
    assert isinstance(small_neg_int, int)
    assert (deserializer.deserialize(NUM_NTSC_FILM_APPROX)
            == Decimal('23.976023976023976023976023976023976024'))
    assert (deserializer.deserialize(NUM_WIDER_THAN_SHORT_FLOAT_REPR)
            == Decimal('1.1000000000000000888178419700125232339'))
    assert (deserializer.deserialize(NUM_TRICKY_PRECISION)
            == 0x1249ad2594c37ceb0b2784c4ce0bf38ace408e211a7caab24308a82e8f10000000000000000000000000)


def test_int_or_float():
    deserializer = Deserializer(
        allow_inexact=True,
        number_type=PythonNumber.INT_OR_FLOAT
    )
    small_int = deserializer.deserialize(NUM_SMALL_INT)
    assert small_int == 42
    assert isinstance(small_int, int)
    small_neg_int = deserializer.deserialize(NUM_SMALL_NEG_INT)
    assert small_neg_int == -42
    assert isinstance(small_neg_int, int)
    assert (deserializer.deserialize(NUM_NTSC_FILM_APPROX)
            == 23.976023976023978)
    assert (deserializer.deserialize(NUM_SHORT_DECIMAL)
            == 1.1)
    assert (deserializer.deserialize(NUM_WIDER_THAN_SHORT_FLOAT_REPR)
            == 1.1)
    assert (deserializer.deserialize(NUM_TRICKY_PRECISION)
            == 0x1249ad2594c37ceb0b2784c4ce0bf38ace408e211a7caab24308a82e8f10000000000000000000000000)


def test_most_compact():
    deserializer = Deserializer(
        allow_inexact=True,
        number_type=PythonNumber.MOST_COMPACT
    )
    small_int = deserializer.deserialize(NUM_SMALL_INT)
    assert small_int == 42
    assert isinstance(small_int, int)
    small_neg_int = deserializer.deserialize(NUM_SMALL_NEG_INT)
    assert small_neg_int == -42
    assert isinstance(small_neg_int, int)
    small_float = deserializer.deserialize(NUM_SHORT_DECIMAL)
    assert small_float == 1.1
    assert isinstance(small_float, float)
    assert (deserializer.deserialize(NUM_NTSC_FILM_APPROX)
            == Decimal('23.976023976023976023976023976023976024'))
    assert (deserializer.deserialize(NUM_WIDER_THAN_SHORT_FLOAT_REPR)
            == Decimal('1.1000000000000000888178419700125232339'))
    assert (deserializer.deserialize(NUM_TRICKY_PRECISION)
            == 0x1249ad2594c37ceb0b2784c4ce0bf38ace408e211a7caab24308a82e8f10000000000000000000000000)
