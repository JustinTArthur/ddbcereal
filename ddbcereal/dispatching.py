from typing import Callable, MutableMapping


class TypedDispatchTable:
    """A less intelligent but faster replacement of functools'
    single dispatch tools.

    Warning: this caches methods for specific types and will grow
    indefinitely as invoke is called with different instance types.
    """

    def __init__(self):
        self._type_methods: MutableMapping[type, Callable] = {}

    def register(self, cls, method):
        self._type_methods[cls] = method

    def invoke(self, instance):
        instance_type = type(instance)
        try:
            return self._type_methods[instance_type](instance)
        except KeyError:
            for type_route, method in self._type_methods.items():
                if issubclass(instance_type, type_route):
                    print(f'Registering {method} for {instance_type}.')
                    self._type_methods[instance_type] = method
                    return method(instance)
            raise NoSuitableMethodForType()


class NoSuitableMethodForType(TypeError):
    pass
