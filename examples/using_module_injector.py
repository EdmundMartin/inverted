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