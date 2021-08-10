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

import enum
from typing import Mapping, Sequence, Union, Any


class DateFormat(enum.Enum):
    UNIX_SECONDS = enum.auto()
    """DynamoDB Number holding number of seconds since the Unix epoch. This is
    the only date/time format that can used as a TTL field for automatic item
    expiration in DynamoDB."""

    UNIX_MILLISECONDS = enum.auto()
    """DynamoDB Number holding number of milliseconds since the Unix epoch."""

    ISO_8601 = enum.auto()
    """DynamoDB String containing an ISO 8601 date string e.g.
    2021-07-18T05:40:59.442117+00:00"""


class DynamoDBType(enum.Enum):
    NUMBER = 'N'
    NUMBER_SET = 'NS'
    STRING = 'S'
    STRING_SET = 'SS'
    BINARY_SET = 'BS'


class PythonNumber(enum.Enum):
    DECIMAL_ONLY = enum.auto()
    """Only use decimal.Decimal. This is the default and the Python equivalent
    of DynamoDB Numbers."""

    FLOAT_ONLY = enum.auto()
    """Convert to Python float, losing accuracy if necessary."""

    FRACTION_ONLY = enum.auto()
    """Convert to fractions.Fraction. Maintains exactness."""

    INT_ONLY = enum.auto()
    """Only use Python ints. Will round if necessary if allow_inexact is True
    """

    INT_OR_DECIMAL = enum.auto()
    """Use int if the Number is whole, otherwise use decimal.Decimal"""

    INT_OR_FLOAT = enum.auto()
    """Use int if the Number is whole, otherwise use a float, losing accuracy
    if necessary."""

    MOST_COMPACT = enum.auto()
    """Use int if the Number is whole, use float if a float's decimal
    character representation matches the number, otherwise use a
    decimal.Decimal."""


DynamoDBTypeSymbol = str
DynamoDBSerialValue = Union[
    bool,
    bytes,
    Mapping[str, Any],
    Sequence[str],
    Sequence[bytes],
    Sequence[Mapping[str, Any]],
    str
]
DynamoDBValue = Mapping[DynamoDBTypeSymbol, DynamoDBSerialValue]
