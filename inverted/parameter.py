import inspect
from typing import Any


class Parameter:

    def __init__(self, name: str, param, keyword_only=False):
        self.name = name
        self.param: inspect.Parameter = param

    @property
    def default_kwarg_value(self) -> (bool, Any):
        #TODO - Proper token parsing for kwarg argument
        return ("=" in str(self.param)), self.param.default

    @property
    def type(self):
        return self.param.annotation
