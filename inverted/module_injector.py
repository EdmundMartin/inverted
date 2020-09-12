from typing import Any, ClassVar, List
import inspect

from inverted.decorators import DecoratorType
from inverted.exceptions import InjectionModuleException, InjectionException
from inverted.parameter import Parameter


class _Singleton:

    def __init__(self, method):
        self._singleton = method()

    def get_injected_value(self):
        return self._singleton


class _Provider:

    def __init__(self, provider_method):
        self._method = provider_method

    def get_injected_value(self):
        return self._method()


class ModuleInjector:

    def __init__(self):
        self._dependencies = {}
        self._supported_param_types = {inspect.Parameter.POSITIONAL_ONLY,
                                       inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                       inspect.Parameter.KEYWORD_ONLY,
                                       inspect.Parameter.VAR_POSITIONAL}

    def __register_typed_singleton(self, func):
        bound_type = func.__annotations__["__inverted_type"]
        if bound_type in self._dependencies:
            raise InjectionModuleException(f"{bound_type} has already been bound to type")
        self._dependencies[bound_type] = _Singleton(func)

    def __register_typed_provider(self, func):
        bound_type = func.__annotations__["__inverted_type"]
        if bound_type in self._dependencies:
            raise InjectionModuleException(f"{bound_type} has already been bound to type")
        self._dependencies[bound_type] = _Provider(func)

    def _register_named_provider(self, func):
        name = func.__annotations__["__inverted_name"]
        if name in self._dependencies:
            raise InjectionModuleException(f"{name} has already been bound")
        self._dependencies[name] = _Provider(func)

    def _handle_registration(self, decorator_type: DecoratorType, func):
        handlers = {DecoratorType.TYPED_SINGLETON: self.__register_typed_singleton,
                    DecoratorType.TYPED: self.__register_typed_provider,
                    DecoratorType.PROVIDES_NAME: self._register_named_provider}
        handlers[decorator_type](func)

    def _extract_arguments(self, klass):
        signature = inspect.signature(klass)
        params = signature.parameters
        results = []
        for param_name, param in params.items():
            if str(param).startswith("*"):
                continue
            if param.kind not in self._supported_param_types:
                raise InjectionException(f"{param.kind} is not supported by inverted")
            if param.name not in self._dependencies and param.annotation == inspect.Parameter.empty:
                raise InjectionException(f"No parameter provided for argument: {param_name}")
            kw_only = param.kind == inspect.Parameter.KEYWORD_ONLY
            results.append(Parameter(param_name, param, keyword_only=kw_only))
        return results

    def _recursively_provide_dependency(self, params: List[Parameter]) -> List[Any]:
        results = []
        for param in params:
            named_resource = self._dependencies.get(param.name)
            typed_resource = self._dependencies.get(param.type)
            if not named_resource and not typed_resource:
                params = self._extract_arguments(param.type)
                injected_params = self._recursively_provide_dependency(params)
                results.append(param.type(*tuple(injected_params)))
            else:
                klass = named_resource or typed_resource
                klass = klass.get_injected_value()
                if not klass:
                    raise InjectionException('Could not create dependency')
                results.append(klass)
        return results

    def _assert_no_parameters(self, func):
        signature = inspect.signature(func)
        if set(signature.parameters.keys()) == {"args", "kwargs"}:
            return
        if len(signature.parameters) > 0:
            raise InjectionModuleException("Providers can not provide arguments")

    def register_provider_module(self, module: ClassVar):
        members = inspect.getmembers(module, predicate=inspect.ismethod)
        for member in members:
            func = member[1]
            if "__inverted_decorator" in func.__annotations__:
                self._assert_no_parameters(func)
                self._handle_registration(func.__annotations__["__inverted_decorator"], func)

    def register_provider_function(self, func):
        if "__inverted_decorator" in func.__annotations__:
            self._assert_no_parameters(func)
            self._handle_registration(func.__annotations__["__inverted_decorator"], func)

    def get_instance(self, klass: ClassVar) -> Any:
        params = self._extract_arguments(klass)
        if len(params) == 0:
            return klass()
        argument_list = self._recursively_provide_dependency(params)
        return klass(*tuple(argument_list))