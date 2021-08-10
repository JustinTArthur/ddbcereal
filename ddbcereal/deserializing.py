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

from binascii import a2b_base64
from collections.abc import Set
from decimal import Decimal
from fractions import Fraction
from typing import (Any, ByteString, Callable, Mapping, MutableMapping,
                    Optional, Sequence, Union)

from ddbcereal.exceptions import NumberInexactError
from ddbcereal.types import (DynamoDBSerialValue, DynamoDBTypeSymbol,
                             DynamoDBValue, PythonNumber)


class Deserializer:
    def __init__(
        self,
        allow_inexact=False,
        raw_transport=False,
        number_type: PythonNumber = PythonNumber.DECIMAL_ONLY,
        null_value: Any = None,
        null_factory: Optional[Callable[[], Any]] = None
    ) -> None:
        if number_type not in inexact_num_deserializers:
            raise ValueError('Unknown python_number technique.')

        if allow_inexact:
            self._deserialize_number = inexact_num_deserializers[number_type]
        elif number_type in exact_num_deserializers:
            self._deserialize_number = exact_num_deserializers[number_type]
        else:
            raise ValueError(f'allow_inexact must be True to use '
                             f'{number_type}')

        _deserialize_binary: Callable
        if raw_transport:
            _deserialize_binary = deserialize_binary_raw
            _deserialize_binary_set = deserialize_binary_set_raw
        else:
            _deserialize_binary = deserialize_binary
            _deserialize_binary_set = deserialize_binary_set

        if null_factory:
            def deserialize_null(serial_value):
                return null_factory()
        else:
            def deserialize_null(serial_value):
                return null_value

        self._deserializers: MutableMapping[DynamoDBTypeSymbol, Callable] = {
            'B': _deserialize_binary,
            'BS': _deserialize_binary_set,
            'BOOL': deserialize_bool,
            'L': self._deserialize_list,
            'M': self._deserialize_map,
            'N': self._deserialize_number,
            'NS': self._deserialize_number_set,
            'NULL': deserialize_null,
            'S': deserialize_string,
            'SS': deserialize_string_set,
        }

    def deserialize(self, value: DynamoDBValue):
        (type_symbol, serial_value), = value.items()
        return self._deserializers[type_symbol](serial_value)

    def deserialize_item(self, item: Mapping[str, DynamoDBValue]) -> Mapping:
        return {
            k: self.deserialize(v) for k, v in item.items()
        }

    def _deserialize_number_set(
        self,
        serial_value: Sequence[str]
    ) -> Set:
        return {self._deserialize_number(n) for n in serial_value}

    def _deserialize_list(
        self,
        serial_value: Sequence[DynamoDBValue]
    ) -> Sequence:
        return [self.deserialize(val) for val in serial_value]

    def _deserialize_map(
        self,
        serial_value: Mapping[str, DynamoDBValue]
    ) -> Mapping:
        return {k: self.deserialize(v) for k, v in serial_value.items()}


def deserialize_binary(serial_value: Union[bytes, memoryview]) -> ByteString:
    return serial_value


def deserialize_binary_raw(serial_value: str) -> ByteString:
    return a2b_base64(serial_value)


def deserialize_binary_set(serial_value: Sequence[DynamoDBSerialValue]) -> Set:
    return {val for val in serial_value}


def deserialize_binary_set_raw(serial_value: Sequence[str]) -> Set:
    return {a2b_base64(val) for val in serial_value}


def deserialize_bool(serial_value: bool) -> bool:
    return serial_value


def deserialize_number_as_decimal(
    serial_value: str
) -> Decimal:
    return Decimal(serial_value)


def deserialize_number_as_exact_int(serial_value: str) -> int:
    try:
        return int(serial_value)
    except ValueError:
        raise NumberInexactError("Can't be represented exactly as an int.")


def deserialize_number_as_int(serial_value: str) -> int:
    try:
        return int(serial_value)
    except ValueError:
        return round(Decimal(serial_value))


def deserialize_number_as_float(serial_value: str) -> float:
    return float(serial_value)


def deserialize_number_as_fraction(
    serial_value: str
) -> Fraction:
    decimal_value = deserialize_number_as_decimal(serial_value)
    return Fraction(*decimal_value.as_integer_ratio())


def deserialize_number_as_most_compact(
    serial_value: str
) -> Union[int, float, Decimal]:
    try:
        return int(serial_value)
    except ValueError:
        float_value = float(serial_value)
        if serial_value == str(float_value):
            # Most compact float representation matches DynamoDB version.
            return float_value

    return Decimal(serial_value)


def deserialize_number_as_int_or_decimal(
    serial_value: str
) -> Union[int, Decimal]:
    try:
        return int(serial_value)
    except ValueError:
        return Decimal(serial_value)


def deserialize_number_as_int_or_float(serial_value: str):
    try:
        return int(serial_value)
    except ValueError:
        return float(serial_value)


def deserialize_string(serial_value: str) -> str:
    return serial_value


def deserialize_string_set(serial_value: Sequence[str]) -> Set:
    return {val for val in serial_value}


exact_num_deserializers = {
    PythonNumber.INT_ONLY: deserialize_number_as_exact_int,
    PythonNumber.INT_OR_DECIMAL: deserialize_number_as_int_or_decimal,
    PythonNumber.DECIMAL_ONLY: deserialize_number_as_decimal,
    PythonNumber.FRACTION_ONLY: deserialize_number_as_fraction,
}
inexact_num_deserializers = {
    PythonNumber.INT_ONLY: deserialize_number_as_int,
    PythonNumber.INT_OR_DECIMAL: deserialize_number_as_int_or_decimal,
    PythonNumber.INT_OR_FLOAT: deserialize_number_as_int_or_float,
    PythonNumber.FLOAT_ONLY: deserialize_number_as_float,
    PythonNumber.DECIMAL_ONLY: deserialize_number_as_decimal,
    PythonNumber.FRACTION_ONLY: deserialize_number_as_fraction,
    PythonNumber.MOST_COMPACT: deserialize_number_as_most_compact
}
