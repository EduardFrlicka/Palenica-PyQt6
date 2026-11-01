"""Errors raised by the database layer.

Each carries a ready-to-display, localised `user_message`, but nothing here
touches the GUI. Presenting the failure - and deciding whether it is fatal - is
the application layer's job (see app.main), which keeps the db package
importable without Qt so headless tooling like create_tables.py can use it.
"""


class DatabaseUnavailable(Exception):
    """The database engine could not be created."""

    def __init__(self, user_message: str):
        super().__init__(user_message)
        self.user_message = user_message


class DatabaseConfigError(DatabaseUnavailable):
    """Configuration is missing or malformed - nothing usable to connect to."""


class DatabaseOffline(DatabaseUnavailable):
    """Configuration is valid but the database could not be reached."""
