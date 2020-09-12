# Inverted
### Work in progress

Dependency injection for modern Python - making use of Python 3 type hints.

## InvertedTypedContainer
```python
from inverted.typed_injector import InvertedTypedContainer

class Dog:
    def __init__(self, name: str):
        self.name = name


class MyPet:
    def __init__(self, ronald: Dog):
        self.val = ronald


class TestClass:

    def __init__(self, hello: str, pet: MyPet):
        self.hello = hello
        self.pet = pet

    def __repr__(self):
        return f"{self.hello} {self.pet}"


if __name__ == '__main__':
    container = InvertedTypedContainer()
    container.bind_to_name_and_type("hello", str, "Привет")
    container.bind_to_name_and_type("name", str, "Ronald")
    result = container.get_instance(TestClass)
```

## InvertedModuleContainer
```python
import sqlite3

from inverted.module_injector import ModuleInjector
from inverted.decorators import provides_named, provides_type


class DatabaseModule:

    def __init__(self, database_name: str):
        self.database_name = database_name

    @provides_named("conn")
    def provide_sqlite_conn(self):
        return sqlite3.connect(self.database_name)

    @provides_type(float)
    def timeout(self):
        return 30.0


class PeopleRepository:

    def __init__(self, conn, timeout: float):
        self.conn = conn
        self.timeout = timeout


if __name__ == '__main__':
    injector = ModuleInjector()
    injector.register_provider_module(DatabaseModule("people.db"))

    people = injector.get_instance(PeopleRepository)
    print(people.conn)  # SQLite Connection
    print(people.timeout)  # 30.0
```