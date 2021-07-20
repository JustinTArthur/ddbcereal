#  Copyright 2021 Justin Arthur
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import decimal
import fractions
from base64 import b64encode
from collections.abc import ByteString, Set
from datetime import datetime
from fractions import Fraction
from typing import Any, Callable, Mapping, MutableMapping, Union

from ddbcereal.exceptions import NumberInexactError, NumberNotAllowedError
from ddbcereal.types import DateFormat, DynamoDBType, DynamoDBValue

NoneType = type(None)


DDB_NUMBER_EMIN = -128
DDB_NUMBER_EMAX = 126
DDB_NUMBER_PREC = 38
INFINITY = decimal.Decimal('Infinity')
NAN = decimal.Decimal('NaN')
NUMBER_TYPES = decimal.Decimal, fractions.Fraction, int, float


class Serializer:
    """For performing many serializations using the same rules
    over time. This maintains a cached map of specific types to their
    most appropriate serializer.
    """
    def __init__(
        self,
        allow_inexact=False,
        validate_numbers=True,
        raw_transport=False,
        datetime_format=DateFormat.ISO_8601,
        fraction_type=DynamoDBType.NUMBER,
    ):
        decimal_traps = [
            decimal.Clamped,
            decimal.Overflow,
            decimal.Underflow
        ]
        if not allow_inexact:
            decimal_traps.append(decimal.Inexact)

        if raw_transport:
            _serialize_bytes = serialize_bytes_raw
        else:
            _serialize_bytes = serialize_bytes

        if validate_numbers:
            serialize_num = self._serialize_number_strict
        else:
            serialize_num = serialize_number
        self._serialize_num = serialize_num

        self._type_methods: MutableMapping[type, Callable] = {
            bool: serialize_bool,
            bytes: _serialize_bytes,
            bytearray: _serialize_bytes,
            memoryview: _serialize_bytes,
            datetime: date_serializers[datetime_format],
            decimal.Decimal: serialize_num,
            dict: self._serialize_mapping,
            float: serialize_num if allow_inexact else serialize_float_exact,
            int: serialize_num,
            list: self._serialize_listlike,
            Mapping: self._serialize_mapping,
            NoneType: serialize_none,
            tuple: self._serialize_listlike,
            frozenset: self._serialize_set,
            set: self._serialize_set,
            str: serialize_str,
        }

        if fraction_type == DynamoDBType.NUMBER:
            self._type_methods[Fraction] = self._serialize_fraction_as_number
        else:
            self._type_methods[Fraction] = serialize_any_as_string

        decimal_ctx = decimal.Context(
            Emin=DDB_NUMBER_EMIN,
            Emax=DDB_NUMBER_EMAX,
            prec=DDB_NUMBER_PREC,
            traps=decimal_traps
        )
        self._decimal_ctx = decimal_ctx
        self._create_decimal = decimal_ctx.create_decimal
        self._decimal_divide = decimal_ctx.divide

    def serialize(self, value: Any) -> DynamoDBValue:
        value_type = type(value)
        try:
            method = self._type_methods[value_type]
        except KeyError:
            for type_route, method in self._type_methods.items():
                if issubclass(value_type, type_route):
                    self._type_methods[value_type] = method
                    return method(value)
        else:
            return method(value)
        raise TypeError('Not a DynamoDB-serializable type.')

    def serialize_item(
        self,
        item: Mapping[str, Any]
    ) -> Mapping[str, DynamoDBValue]:
        return {k: self.serialize(v) for k, v in item.items()}

    def _serialize_fraction_as_number(self, value: Fraction):
        try:
            return {
                'N': str(self._decimal_divide(value.numerator,
                                              value.denominator))}
        except decimal.Inexact:
            raise NumberInexactError()

    def _serialize_number_strict(
        self,
        value: Union[int, float, decimal.Decimal]
    ):
        try:
            dec_value = self._create_decimal(str(value))
        except decimal.Inexact:
            raise NumberInexactError()
        if dec_value in (INFINITY, NAN):
            raise NumberNotAllowedError(f'{dec_value} not supported')
        return {'N': str(dec_value)}

    def _serialize_listlike(self, value: Union[list, tuple]):
        return {'L': [self.serialize(element) for element in value]}

    def _serialize_set(self, value: Set):
        if all(isinstance(element, str) for element in value):
            return {'SS': [element for element in value]}
        if all(isinstance(element, NUMBER_TYPES) for element in value):
            return {
                'NS': [
                    val
                    for element in value
                    for val in self.serialize(element).values()
                ]
            }
        if all(isinstance(element, ByteString) for element in value):
            return {
                'BS': [
                    val
                    for element in value
                    for val in self.serialize(element).values()
                ]
            }

    def _serialize_mapping(self, value: Mapping):
        return {
            'M': {k: self.serialize(v) for k, v in value.items()}
        }


def serialize_bool(value: bool):
    return {'BOOL': value}


def serialize_bytes(value: ByteString):
    return {'B': value}


def serialize_bytes_raw(value: Union[bytes, memoryview]):
    return {'B': b64encode(value).decode('ascii')}


def serialize_number(value):
    return {'N': str(value)}


def serialize_none(value: NoneType):
    return {'NULL': True}


def serialize_float_exact(value: float):
    raise NumberInexactError('Floats are inexact by nature.')


def serialize_any_as_string(value: Any):
    return {'S': str(value)}


def serialize_str(value: str):
    return {'S': value}


def serialize_datetime_as_unix_seconds(value: datetime):
    return {'N': str(value.timestamp())}


def serialize_datetime_as_unix_milliseconds(value: datetime):
    return {'N': str(value.timestamp() * 1000.0)}


def serialize_datetime_as_iso_8601_string(value: datetime):
    return {'S': value.isoformat()}


date_serializers = {
    DateFormat.UNIX_SECONDS: serialize_datetime_as_unix_seconds,
    DateFormat.UNIX_MILLISECONDS: serialize_datetime_as_unix_milliseconds,
    DateFormat.ISO_8601: serialize_datetime_as_iso_8601_string
}
