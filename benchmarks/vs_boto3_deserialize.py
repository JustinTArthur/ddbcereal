from timeit import timeit

from boto3.dynamodb.types import TypeDeserializer as Boto3Deserializer

from ddbcereal import Deserializer as DDBCerealDeserializer

SIMPLE_DECIMAL = {'N': '123456789.0123456789'}
SMALL_INT = {'N': '1937531'}
SMALL_STR = {'S': '5358ab8b-d9dd-4c1f-9160-f0f63ebd627a'}
SMALL_NUMBER_SET = {'NS': ['123', '456', '789', '10.123456789']}
SMALL_STR_SET = {
    'SS': [
        '2f0b93e4-6b5e-4c8a-bcf2-75fa9f4b2774',
        '6a45c460-5e80-4b9d-b180-6793b7556222',
        '797cd758-c737-4346-906e-86c6def63885',
        'cced0ae6-1bf4-4403-93a4-8a4ed3dd64a3',
        'fd0e0011-c978-4245-88a9-b6013e43762b'
    ]
}
MIXED_LIST = {'L': [SMALL_INT, SMALL_STR, SIMPLE_DECIMAL, {'BOOL': True}, {'NULL': True}]}
MIXED_MAP = {
    'M': {
        'attrA': SMALL_INT,
        'attrB': SMALL_STR,
        'attrC': {'BOOL': False}
    }
}
MIXED_MAP_2_LVL = {
    'M': {
        'attrA': SMALL_INT,
        'attrB': SMALL_STR,
        'attrC': {
            'M' : {
                'attrA': SMALL_INT,
                'attrB': SMALL_STR,
            }
        }
    }
}

boto3_deserializer = Boto3Deserializer()
ddbcereal_deserializer = DDBCerealDeserializer(allow_inexact=False)


def main():
    print('Deserializer Construction')
    print(f'boto3: {timeit(Boto3Deserializer)}')
    print(f'ddbcereal: {timeit(DDBCerealDeserializer)}')

    print('Number to Decimal')
    print(f'boto3: '
          f'{timeit(lambda: boto3_deserializer.deserialize(SIMPLE_DECIMAL))}')
    print(f'ddbcereal: '
          f'{timeit(lambda: ddbcereal_deserializer.deserialize(SIMPLE_DECIMAL))}')

    print('Integer Number to Decimal')
    print(f'boto3: {timeit(lambda: boto3_deserializer.deserialize(SMALL_INT))}')
    print(f'ddbcereal: '
          f'{timeit(lambda: ddbcereal_deserializer.deserialize(SMALL_INT))}')

    print('String to str')
    print(f'boto3: {timeit(lambda: boto3_deserializer.deserialize(SMALL_STR))}')
    print(f'ddbcereal: '
          f'{timeit(lambda: ddbcereal_deserializer.deserialize(SMALL_STR))}')

    print('Number Set to Mixed number types Set')
    print(f'boto3: '
          f'{timeit(lambda: boto3_deserializer.deserialize(SMALL_NUMBER_SET))}')
    print(f'ddbcereal: '
          f'{timeit(lambda: ddbcereal_deserializer.deserialize(SMALL_NUMBER_SET))}')

    print('String Set to set[str]')
    print(f'boto3: '
          f'{timeit(lambda: boto3_deserializer.deserialize(SMALL_STR_SET))}')
    print(f'ddbcereal: '
          f'{timeit(lambda: ddbcereal_deserializer.deserialize(SMALL_STR_SET))}')

    print('List to List of mixed types')
    print(f'boto3: {timeit(lambda: boto3_deserializer.deserialize(MIXED_LIST))}')
    print(f'ddbcereal: '
          f'{timeit(lambda: ddbcereal_deserializer.deserialize(MIXED_LIST))}')

    print('Map of mixed types to dict')
    print(f'boto3: {timeit(lambda: boto3_deserializer.deserialize(MIXED_MAP))}')
    print(f'ddbcereal: '
          f'{timeit(lambda: ddbcereal_deserializer.deserialize(MIXED_MAP))}')

    print('Map of 2 levels to dict')
    print(f'boto3: '
          f'{timeit(lambda: boto3_deserializer.deserialize(MIXED_MAP_2_LVL))}')
    print(f'ddbcereal: '
          f'{timeit(lambda: ddbcereal_deserializer.deserialize(MIXED_MAP_2_LVL))}')


if __name__ == '__main__':
    main()
