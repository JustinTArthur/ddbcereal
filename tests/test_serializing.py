from decimal import Decimal
from fractions import Fraction

import pytest

from ddbcereal import NumberInexact
from ddbcereal.serializing import Serializer
from ddbcereal.types import DynamoDBType

BIG_VALID_INT = (
    10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
)
BIG_INVALID_INT = (
    10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001
) 
BIG_INVALID_DECIMAL = Decimal(BIG_INVALID_INT)


def test_ints():
    serializer = Serializer()
    assert serializer.serialize(42) == {'N': '42'}
    assert serializer.serialize(0) == {'N': '0'}


def test_decimals():
    serializer = Serializer()
    assert serializer.serialize(Decimal('1.2345')) == {'N': '1.2345'}
    assert serializer.serialize(Decimal('0')) == {'N': '0'}


def test_strs():
    serializer = Serializer()
    assert serializer.serialize('9873') == {'S': '9873'}
    assert serializer.serialize('abc def') == {'S': 'abc def'}
    nullify_serializer = Serializer(nullify_empty_string=True)
    assert nullify_serializer.serialize('') == {'NULL': True}


def test_number_validation():
    inexact_serializer = Serializer(allow_inexact=True)
    exact_serializer = Serializer(allow_inexact=False)
    exact_lax_serializer = Serializer(allow_inexact=False, validate_numbers=False)

    # These will truncate insignificant digits to meet precision:
    assert (inexact_serializer.serialize(BIG_VALID_INT)
            == {'N': '1.0000000000000000000000000000000000000E+100'})
    assert (exact_serializer.serialize(BIG_VALID_INT)
            == {'N': '1.0000000000000000000000000000000000000E+100'})

    # This will truncate/round significant digits to meet precision:
    assert (inexact_serializer.serialize(BIG_INVALID_INT)
            == {'N': '1.0000000000000000000000000000000000000E+100'})

    with pytest.raises(NumberInexact):
        exact_serializer.serialize(BIG_INVALID_INT)

    assert (exact_lax_serializer.serialize(BIG_INVALID_INT)
            == {'N': '10000000000000000000000000000000000000000000000000000000'
                     '000000000000000000000000000000000000000000001'})
    assert (exact_lax_serializer.serialize(BIG_INVALID_DECIMAL)
            == {'N': '10000000000000000000000000000000000000000000000000000000'
                     '000000000000000000000000000000000000000000001'})


def test_fractions():
    inexact_serializer = Serializer(allow_inexact=True)
    exact_serializer = Serializer(allow_inexact=False)
    string_serializer = Serializer(fraction_type=DynamoDBType.STRING)

    common_film_rate = Fraction(24, 1)
    ntsc_film_rate = Fraction(24000, 1001)

    assert inexact_serializer.serialize(common_film_rate) == {'N': '24'}
    assert exact_serializer.serialize(common_film_rate) == {'N': '24'}
    assert string_serializer.serialize(common_film_rate) == {'S': '24'}

    assert (inexact_serializer.serialize(ntsc_film_rate)
            == {'N': '23.976023976023976023976023976023976024'})
    with pytest.raises(NumberInexact):
        exact_serializer.serialize(ntsc_film_rate)
    assert string_serializer.serialize(ntsc_film_rate) == {'S': '24000/1001'}



def test_none():
    serializer = Serializer()
    return serializer.serialize(None) == {'NULL': True}


def test_bools():
    serializer = Serializer()
    assert serializer.serialize(True) == {'BOOL': True}
    assert serializer.serialize(False) == {'BOOL': False}


def test_lists():
    serializer = Serializer()
    assert serializer.serialize([1, 'abc', None, None, True]) == {
        'L': [{'N': '1'}, {'S': 'abc'}, {'NULL': True}, {'NULL': True},
              {'BOOL': True}]
    }


def test_sets():
    serializer = Serializer(allow_inexact=True)
    serialized_ns = serializer.serialize({1, 2, 3, 5.45, Decimal('6.75')})
    assert serialized_ns.keys() == {'NS'}
    assert set(serialized_ns['NS']) == {'1', '2', '3', '5.45', '6.75'}

    serialized_ns = serializer.serialize(
        frozenset((1, 2, 3, 5.45, Decimal('6.75')))
    )
    assert serialized_ns.keys() == {'NS'}
    assert set(serialized_ns['NS']) == {'1', '2', '3', '5.45', '6.75'}

    serialized_ss = serializer.serialize({'123', 'abc'})
    assert serialized_ss.keys() == {'SS'}
    assert set(serialized_ss['SS']) == {'123', 'abc'}


def test_maps():
    serializer = Serializer()
    assert serializer.serialize({
        'this': 'that',
        'another': 123,
        'level2': {'isTrue': True}
    }) == {
        'M': {
            'this': {'S': 'that'},
            'another': {'N': '123'},
            'level2': {'M': {'isTrue': {'BOOL': True}}}
        }
    }

