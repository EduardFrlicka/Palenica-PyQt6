"""SQLAlchemy dialect for Turso, built on the `libsql` package.

Registers the ``sqlite+turso://`` URL scheme:

    sqlite+turso://<host>/?authToken=<jwt>         remote Turso database
    sqlite+turso:///path/to/local.db               plain local file

Why not the published `sqlalchemy-libsql` package: it requires
`libsql-experimental`, which has never published a Windows wheel, so
`pip install -r requirements.txt` cannot succeed on the windows-latest runner
that builds the release executables. `libsql` is the maintained successor and
does ship win_amd64 wheels. The scheme is named `turso` rather than `libsql`
so it can never collide with `sqlalchemy-libsql`, which claims
``sqlite+libsql`` through an entry point if it happens to be installed.

`libsql` is a close relative of `sqlite3`, but it is not a complete DB-API
module: it exposes no exception hierarchy (every failure arrives as a bare
``ValueError``) and omits a few module level constants the pysqlite dialect
reads. This module fills both gaps so the stock dialect can be reused, and
translates driver errors into DB-API classes so SQLAlchemy can tell an
integrity violation from a dropped connection.
"""

import libsql
from sqlalchemy.dialects import registry
from sqlalchemy.dialects.sqlite.pysqlite import SQLiteDialect_pysqlite


class Error(Exception):
    pass


class InterfaceError(Error):
    pass


class DatabaseError(Error):
    pass


class DataError(DatabaseError):
    pass


class OperationalError(DatabaseError):
    pass


class IntegrityError(DatabaseError):
    pass


class InternalError(DatabaseError):
    pass


class ProgrammingError(DatabaseError):
    pass


class NotSupportedError(DatabaseError):
    pass


# A remote failure arrives wrapped in a Hrana envelope that still quotes the
# underlying SQLite message, e.g.
#   Hrana: `stream error: `Error { message: "SQLite error: UNIQUE constraint
#   failed: production_line.name", code: "SQLITE_CONSTRAINT" }``
# so the constraint markers must be tested before the transport ones.
_INTEGRITY_MARKERS = (
    "sqlite_constraint",
    "constraint failed",
    "primary key must be unique",
)

_DISCONNECT_MARKERS = (
    "stream expired",
    "stream not found",
    "baton",
    "connection reset",
    "connection refused",
    "connection closed",
    "broken pipe",
    "error sending request",
    "failed to lookup address",
    "dns error",
    "timed out",
    "status=500",
    "status=502",
    "status=503",
    "status=504",
    "cannot operate on a closed database",
)


def _classify(message: str):
    lowered = message.lower()
    if any(marker in lowered for marker in _INTEGRITY_MARKERS):
        return IntegrityError
    # Everything else - bad SQL, missing table, locked database, transport
    # failure - matches what sqlite3 reports as OperationalError.
    return OperationalError


def _translate(exc: BaseException) -> BaseException:
    """Map a raw libsql failure onto the DB-API exception hierarchy."""
    if isinstance(exc, Error):
        return exc
    return _classify(str(exc))(str(exc)).with_traceback(exc.__traceback__)


class _DBAPI:
    """`libsql`, padded out to the parts of the DB-API SQLAlchemy touches."""

    Error = Error
    Warning = Warning
    InterfaceError = InterfaceError
    DatabaseError = DatabaseError
    DataError = DataError
    OperationalError = OperationalError
    IntegrityError = IntegrityError
    InternalError = InternalError
    ProgrammingError = ProgrammingError
    NotSupportedError = NotSupportedError

    Connection = libsql.Connection
    Cursor = libsql.Cursor
    connect = staticmethod(libsql.connect)

    paramstyle = libsql.paramstyle
    apilevel = "2.0"
    threadsafety = 1
    sqlite_version_info = libsql.sqlite_version_info
    sqlite_version = ".".join(str(part) for part in libsql.sqlite_version_info)


class SQLiteDialect_turso(SQLiteDialect_pysqlite):
    driver = "turso"
    supports_statement_cache = SQLiteDialect_pysqlite.supports_statement_cache

    @classmethod
    def import_dbapi(cls):
        return _DBAPI

    def on_connect(self):
        # The pysqlite hook only installs create_function() based helpers,
        # which libsql does not support.
        return None

    def _get_server_version_info(self, connection):
        return _DBAPI.sqlite_version_info

    def create_connect_args(self, url):
        query = dict(url.query)
        # Accepted and ignored: the libsql:// scheme is TLS either way.
        query.pop("secure", None)
        auth_token = query.pop("authToken", None) or query.pop("auth_token", None)

        if url.host:
            netloc = f"{url.host}:{url.port}" if url.port else url.host
            database = f"libsql://{netloc}"
            if url.database:
                database += f"/{url.database}"
        else:
            database = url.database or ":memory:"

        kwargs = {}
        if auth_token:
            kwargs["auth_token"] = auth_token
        return ([database], kwargs)

    def connect(self, *args, **kwargs):
        try:
            return super().connect(*args, **kwargs)
        except Exception as exc:
            raise _translate(exc) from None

    def do_execute(self, cursor, statement, parameters, context=None):
        try:
            cursor.execute(statement, parameters)
        except Exception as exc:
            raise _translate(exc) from None

    def do_execute_no_params(self, cursor, statement, context=None):
        try:
            cursor.execute(statement)
        except Exception as exc:
            raise _translate(exc) from None

    def do_executemany(self, cursor, statement, parameters, context=None):
        try:
            cursor.executemany(statement, parameters)
        except Exception as exc:
            raise _translate(exc) from None

    def do_commit(self, dbapi_connection):
        try:
            dbapi_connection.commit()
        except Exception as exc:
            raise _translate(exc) from None

    def do_rollback(self, dbapi_connection):
        try:
            dbapi_connection.rollback()
        except Exception as exc:
            raise _translate(exc) from None

    def do_ping(self, dbapi_connection):
        try:
            return super().do_ping(dbapi_connection)
        except Exception as exc:
            raise _translate(exc) from None

    def is_disconnect(self, e, connection, cursor):
        lowered = str(e).lower()
        if any(marker in lowered for marker in _INTEGRITY_MARKERS):
            return False
        return any(marker in lowered for marker in _DISCONNECT_MARKERS)


registry.register("sqlite.turso", __name__, "SQLiteDialect_turso")

dialect = SQLiteDialect_turso
