from decimal import Decimal
from timeit import timeit

setup = 'from decimal import Decimal\nd1=Decimal("12.3456789")'


def with_str(value: Decimal):
    return str(value)


def with_f_string(value: Decimal):
    return f'{value}'


if __name__ == '__main__':
    print(timeit('a=f(d1)', setup, number=10_000_000, globals={'f': with_str}))
    print(timeit('a=f(d1)', setup, number=10_000_000, globals={'f': with_f_string}))
