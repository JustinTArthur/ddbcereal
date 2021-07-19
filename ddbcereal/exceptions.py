class NumberRepresentationError(ValueError):
    pass


class NumberInexact(NumberRepresentationError):
    pass


class NumberRounded(NumberRepresentationError):
    pass


class NumberNotAllowed(NumberRepresentationError):
    pass


class StringNotAllowed(ValueError):
    pass
