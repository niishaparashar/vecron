import os
from collections.abc import Iterator, Sequence
from typing import Any

import psycopg


class Row(Sequence[Any]):
    """A psycopg result row with legacy positional and named access."""

    def __init__(self, columns: tuple[str, ...], values: tuple[Any, ...]):
        self._columns = columns
        self._values = values
        self._index = {column: index for index, column in enumerate(columns)}

    def __getitem__(self, key: int | slice | str) -> Any:
        if isinstance(key, str):
            return self._values[self._index[key]]
        return self._values[key]

    def __len__(self) -> int:
        return len(self._values)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._values)

    def keys(self) -> tuple[str, ...]:
        return self._columns


class Cursor:
    """Translate qmark parameters and return compatible rows."""

    def __init__(self, cursor: psycopg.Cursor):
        self._cursor = cursor

    @staticmethod
    def _translate(sql: str) -> str:
        return sql.replace("?", "%s")

    def execute(self, sql: str, params: Any = None):
        if params is None:
            self._cursor.execute(self._translate(sql))
        else:
            self._cursor.execute(self._translate(sql), params)
        return self

    def executemany(self, sql: str, params: Any):
        self._cursor.executemany(self._translate(sql), params)
        return self

    def _row(self, values: tuple[Any, ...] | None) -> Row | None:
        if values is None:
            return None
        columns = tuple(description.name for description in self._cursor.description or ())
        return Row(columns, values)

    def fetchone(self) -> Row | None:
        return self._row(self._cursor.fetchone())

    def fetchmany(self, size: int | None = None) -> list[Row]:
        rows = self._cursor.fetchmany() if size is None else self._cursor.fetchmany(size)
        return [self._row(row) for row in rows]

    def fetchall(self) -> list[Row]:
        return [self._row(row) for row in self._cursor.fetchall()]

    def __iter__(self) -> Iterator[Row]:
        for row in self._cursor:
            wrapped = self._row(row)
            if wrapped is not None:
                yield wrapped

    def __getattr__(self, name: str) -> Any:
        return getattr(self._cursor, name)


class Connection:
    """Expose the connection methods used by the application."""

    def __init__(self, connection: psycopg.Connection):
        self._connection = connection

    def cursor(self) -> Cursor:
        return Cursor(self._connection.cursor())

    def commit(self) -> None:
        self._connection.commit()

    def rollback(self) -> None:
        self._connection.rollback()

    def close(self) -> None:
        self._connection.close()


def get_db() -> Connection:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL must be configured for PostgreSQL access")
    return Connection(psycopg.connect(database_url))
