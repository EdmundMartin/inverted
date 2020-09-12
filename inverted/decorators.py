from enum import Enum
import functools
from typing import Type


class DecoratorType(Enum):
    TYPED_SINGLETON = "Typed Singleton"
    TYPED = "Typed"
    PROVIDES_NAME = "Provides Name"


def typed_singleton(singleton_type: Type):
    def inner_decorator(f):
        def wrapped(*args, **kwargs):
            response = f(*args, **kwargs)
            return response
        wrapped.__annotations__["__inverted_decorator"] = DecoratorType.TYPED_SINGLETON
        wrapped.__annotations__["__inverted_type"] = singleton_type
        return wrapped
    return inner_decorator


def provides_type(provided_type: Type):
    def inner_decorator(f):
        def wrapped(*args, **kwargs):
            response = f(*args, **kwargs)
            return response
        wrapped.__annotations__["__inverted_decorator"] = DecoratorType.TYPED
        wrapped.__annotations__["__inverted_type"] = provided_type
        return wrapped
    return inner_decorator


def provides_named(provided_name: str):
    def inner_decorator(f):
        def wrapped(*args, **kwargs):
            response = f(*args, **kwargs)
            return response
        wrapped.__annotations__["__inverted_decorator"] = DecoratorType.PROVIDES_NAME
        wrapped.__annotations__["__inverted_name"] = provided_name
        return wrapped
    return inner_decorator

