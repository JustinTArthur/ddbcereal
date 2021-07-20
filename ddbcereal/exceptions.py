class NumberInexactError(ValueError):
    """A supplied number can't be represented exactly by the target type and
    would either lose intent or data."""


class NumberNotAllowedError(ValueError):
    """A supplied number can't be stored by DynamoDB."""
