import inspect
from typing import Any, ClassVar, List, Type

from inverted.parameter import Parameter
from inverted.exceptions import InjectionException


class InvertedTypedContainer:

    def __init__(self):
        self._named_typed_resources = {}
        self._typed_resources = {}
        self._supported_param_types = {inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD}

    def bind_to_name_and_type(self, name: str, resource_type: Type, resource: Any) -> None:
        self._named_typed_resources[(name, resource_type)] = resource

    def bind_to_type(self, resource_type: Type, resource: Any):
        self._typed_resources[resource_type] = resource

    def _extract_arguments(self, klass):
        signature = inspect.signature(klass)
        params = signature.parameters
        results = []
        for param_name, param in params.items():
            if param.kind not in self._supported_param_types:
                raise InjectionException(f"{param.kind} is not supported by inverted")
            if param.annotation == inspect.Parameter.empty:
                raise InjectionException(f"No parameter provided for argument: {param_name}")
            results.append(Parameter(param_name, param))
        return results

    def _recursively_provide_dependency(self, params: List[Parameter]) -> List[Any]:
        results = []
        for param in params:
            named_resource = self._named_typed_resources.get((param.name, param.type))
            typed_resource = self._typed_resources.get(param.type)
            if not named_resource and not typed_resource:
                params = self._extract_arguments(param.type)
                injected_params = self._recursively_provide_dependency(params)
                results.append(param.type(*tuple(injected_params)))
            else:
                klass = named_resource or typed_resource
                if not klass:
                    raise InjectionException('Could not create dependency')
                results.append(klass)
        return results

    def get_instance(self, klass: ClassVar) -> Any:
        params = self._extract_arguments(klass)
        if len(params) == 0:
            return klass()
        argument_list = self._recursively_provide_dependency(params)
        return klass(*tuple(argument_list))


