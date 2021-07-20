from decimal import Decimal
from timeit import timeit

from boto3.dynamodb.types import TypeSerializer as Boto3Serializer

from ddbcereal import Serializer as DDBCerealSerializer

SIMPLE_DECIMAL = Decimal('123456789.0123456789')
SMALL_INT = 1937531
SMALL_STR = '5358ab8b-d9dd-4c1f-9160-f0f63ebd627a'
SMALL_NUMBER_SET = {123, 456, 789, Decimal('10.123456789')}
SMALL_STR_SET = {
    '2f0b93e4-6b5e-4c8a-bcf2-75fa9f4b2774',
    '6a45c460-5e80-4b9d-b180-6793b7556222',
    '797cd758-c737-4346-906e-86c6def63885',
    'cced0ae6-1bf4-4403-93a4-8a4ed3dd64a3',
    'fd0e0011-c978-4245-88a9-b6013e43762b'
}
MIXED_LIST = [SMALL_INT, SMALL_STR, SIMPLE_DECIMAL, True, None]
MIXED_DICT = {
    'attrA': SMALL_INT,
    'attrB': SMALL_STR,
    'attrC': False
}
MIXED_DICT_2_LVL = {
    'attrA': SMALL_INT,
    'attrB': SMALL_STR,
    'attrC': {
        'attrA': SMALL_INT,
        'attrB': SMALL_STR,
    }
}

boto3_serializer = Boto3Serializer()
ddbcereal_serializer = DDBCerealSerializer(allow_inexact=False)
ddbcereal_nonvalidating = DDBCerealSerializer(
    validate_numbers=False
)


def main():
    print('Serializer Construction')
    print(f'boto3: {timeit(Boto3Serializer)}')
    print(f'ddbcereal: {timeit(DDBCerealSerializer)}')

    print('Decimal to Number')
    print(f'boto3: '
          f'{timeit(lambda: boto3_serializer.serialize(SIMPLE_DECIMAL))}')
    print(f'ddbcereal: '
          f'{timeit(lambda: ddbcereal_serializer.serialize(SIMPLE_DECIMAL))}')
    print(f'ddbcereal non-validating: '
          f'{timeit(lambda: ddbcereal_nonvalidating.serialize(SIMPLE_DECIMAL))}')

    print('int to Number')
    print(f'boto3: {timeit(lambda: boto3_serializer.serialize(SMALL_INT))}')
    print(f'ddbcereal: '
          f'{timeit(lambda: ddbcereal_serializer.serialize(SMALL_INT))}')
    print(f'ddbcereal non-validating: '
          f'{timeit(lambda: ddbcereal_nonvalidating.serialize(SMALL_INT))}')

    print('str to String')
    print(f'boto3: {timeit(lambda: boto3_serializer.serialize(SMALL_STR))}')
    print(f'ddbcereal: '
          f'{timeit(lambda: ddbcereal_serializer.serialize(SMALL_STR))}')
    print(
        f'ddbcereal non-validating: '
        f'{timeit(lambda: ddbcereal_nonvalidating.serialize(SMALL_STR))}')

    print('Mixed number types Set to Number Set')
    print(f'boto3: '
          f'{timeit(lambda: boto3_serializer.serialize(SMALL_NUMBER_SET))}')
    print(f'ddbcereal: '
          f'{timeit(lambda: ddbcereal_serializer.serialize(SMALL_NUMBER_SET))}')
    print(
        f'ddbcereal non-validating: '
        f'{timeit(lambda: ddbcereal_nonvalidating.serialize(SMALL_NUMBER_SET))}')

    print('Set[str] to String Set')
    print(f'boto3: '
          f'{timeit(lambda: boto3_serializer.serialize(SMALL_STR_SET))}')
    print(f'ddbcereal: '
          f'{timeit(lambda: ddbcereal_serializer.serialize(SMALL_STR_SET))}')
    print(
        f'ddbcereal non-validating: '
        f'{timeit(lambda: ddbcereal_nonvalidating.serialize(SMALL_STR_SET))}')

    print('List of mixed types to List')
    print(f'boto3: {timeit(lambda: boto3_serializer.serialize(MIXED_LIST))}')
    print(f'ddbcereal: '
          f'{timeit(lambda: ddbcereal_serializer.serialize(MIXED_LIST))}')
    print(
        f'ddbcereal non-validating: '
        f'{timeit(lambda: ddbcereal_nonvalidating.serialize(MIXED_LIST))}')

    print('dict of mixed types to Map')
    print(f'boto3: {timeit(lambda: boto3_serializer.serialize(MIXED_DICT))}')
    print(f'ddbcereal: '
          f'{timeit(lambda: ddbcereal_serializer.serialize(MIXED_DICT))}')
    print(
        f'ddbcereal non-validating: '
        f'{timeit(lambda: ddbcereal_nonvalidating.serialize(MIXED_DICT))}')

    print('dict of 2 levels to Map')
    print(f'boto3: '
          f'{timeit(lambda: boto3_serializer.serialize(MIXED_DICT_2_LVL))}')
    print(f'ddbcereal: '
          f'{timeit(lambda: ddbcereal_serializer.serialize(MIXED_DICT_2_LVL))}')
    print(
        f'ddbcereal non-validating: '
        f'{timeit(lambda: ddbcereal_nonvalidating.serialize(MIXED_DICT_2_LVL))}')


if __name__ == '__main__':
    main()
