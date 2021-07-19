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

from collections.abc import Set
from decimal import Decimal
from fractions import Fraction
from typing import (Any, ByteString, Callable, Mapping, MutableMapping,
                    Sequence, Union)

from ddbcereal import NumberInexact
from ddbcereal.types import PythonNumber

DynamoDBTypeSymbol = str  # Literal['B', 'BOOL', 'BS', 'N', 'NS', 'S', 'SS', 'L', 'M', 'NULL']
DynamoDBSerialValue = Union[
    bool,
    bytes,
    Mapping,
    Sequence[str],
    Sequence[bytes],
    Sequence[Mapping],
    str
]
DynamoDBValue = Mapping[DynamoDBTypeSymbol, DynamoDBSerialValue]


class Deserializer:
    def __init__(
        self,
        allow_inexact=False,
        number_type: PythonNumber = PythonNumber.DECIMAL_ONLY,
        null_value: Any = None,
        null_factory: Callable[[], Any] = None
    ):
        if number_type not in inexact_num_deserializers:
            raise ValueError('Unknown python_number technique.')

        if allow_inexact:
            self._deserialize_number = inexact_num_deserializers[number_type]
        elif number_type in exact_num_deserializers:
            self._deserialize_number = exact_num_deserializers[number_type]
        else:
            raise ValueError(f'allow_inexact must be True to use '
                             f'{number_type}')

        self._deserializers: MutableMapping[
            DynamoDBTypeSymbol,
            Callable[[DynamoDBSerialValue], ...]
        ] = {
            'B': deserialize_binary,
            'BS': deserialize_binary_set,
            'BOOL': deserialize_bool,
            'L': self._deserialize_list,
            'M': self._deserialize_map,
            'N': self._deserialize_number,
            'NS': self._deserialize_number_set,
            'NULL': null_factory or (lambda val: null_value),
            'S': deserialize_string,
            'SS': deserialize_string_set,
        }

    def deserialize(self, value: DynamoDBValue):
        (type_symbol, serial_value), = value.items()
        return self._deserializers[type_symbol](serial_value)

    def deserialize_item(self, item):
        return {
            k: self.deserialize(v) for k, v in item.items()
        }

    def _deserialize_number_set(
        self,
        serial_value: DynamoDBSerialValue
    ) -> Set:
        return {self._deserialize_number(n) for n in serial_value}

    def _deserialize_list(self, serial_value: DynamoDBSerialValue) -> Sequence:
        return [self.deserialize(val) for val in serial_value]

    def _deserialize_map(self, serial_value: DynamoDBSerialValue) -> Mapping:
        return {k: self.deserialize(v) for k, v in serial_value.items()}


def deserialize_binary(serial_value: DynamoDBSerialValue) -> ByteString:
    return serial_value


def deserialize_binary_set(serial_value: DynamoDBSerialValue) -> Set:
    return {val for val in serial_value}


def deserialize_bool(serial_value: DynamoDBSerialValue) -> bool:
    return serial_value


def deserialize_number_as_decimal(
    serial_value: DynamoDBSerialValue
) -> Decimal:
    return Decimal(serial_value)


def deserialize_number_as_exact_int(serial_value: DynamoDBSerialValue) -> int:
    try:
        return int(serial_value)
    except ValueError:
        raise NumberInexact("Can't be represented exactly as an int.")


def deserialize_number_as_int(serial_value: DynamoDBSerialValue) -> int:
    try:
        return int(serial_value)
    except ValueError:
        return round(Decimal(serial_value))


def deserialize_number_as_float(serial_value: DynamoDBSerialValue) -> float:
    return float(serial_value)


def deserialize_number_as_fraction(
    serial_value: DynamoDBSerialValue
) -> Fraction:
    decimal_value = deserialize_number_as_decimal(serial_value)
    return Fraction(*decimal_value.as_integer_ratio())


def deserialize_number_as_most_compact(
    serial_value: DynamoDBSerialValue
) -> Union[int, float, Decimal]:
    try:
        return int(serial_value)
    except ValueError:
        float_value = float(serial_value)
        if serial_value == str(float_value):
            # Most compact float representation matches DynamoDB version.
            return float_value

    return Decimal(serial_value)


def deserialize_number_as_int_or_decimal(serial_value: DynamoDBSerialValue):
    try:
        return int(serial_value)
    except ValueError:
        return Decimal(serial_value)


def deserialize_number_as_int_or_float(serial_value: DynamoDBSerialValue):
    try:
        return int(serial_value)
    except ValueError:
        return float(serial_value)


def deserialize_string(serial_value: DynamoDBSerialValue) -> str:
    return serial_value


def deserialize_string_set(serial_value: DynamoDBSerialValue) -> Set:
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
