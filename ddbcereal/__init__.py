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

from ddbcereal.deserializing import Deserializer
from ddbcereal.exceptions import NumberInexactError, NumberNotAllowedError
from ddbcereal.serializing import Serializer
from ddbcereal.types import DateFormat, DynamoDBType, PythonNumber

VERSION = 2, 1, 1

ISO_8601 = DateFormat.ISO_8601
UNIX_MILLISECONDS = DateFormat.UNIX_MILLISECONDS
UNIX_SECONDS = DateFormat.UNIX_SECONDS

BINARY_SET = DynamoDBType.BINARY_SET
NUMBER = DynamoDBType.NUMBER
NUMBER_SET = DynamoDBType.NUMBER_SET
STRING = DynamoDBType.STRING
STRING_SET = DynamoDBType.STRING_SET

DECIMAL_ONLY = PythonNumber.DECIMAL_ONLY
FLOAT_ONLY = PythonNumber.FLOAT_ONLY
FRACTION_ONLY = PythonNumber.FRACTION_ONLY
INT_ONLY = PythonNumber.INT_ONLY
INT_OR_DECIMAL = PythonNumber.INT_OR_DECIMAL
INT_OR_FLOAT = PythonNumber.INT_OR_FLOAT
MOST_COMPACT = PythonNumber.MOST_COMPACT

__all__ = ('DateFormat', 'DECIMAL_ONLY', 'Deserializer', 'DynamoDBType',
           'FLOAT_ONLY', 'FRACTION_ONLY', 'INT_ONLY', 'INT_OR_DECIMAL',
           'INT_OR_FLOAT', 'ISO_8601', 'MOST_COMPACT', 'NUMBER',
           'NumberInexactError', 'NumberNotAllowedError', 'PythonNumber',
           'Serializer', 'STRING', 'UNIX_MILLISECONDS', 'UNIX_SECONDS',
           'VERSION')
