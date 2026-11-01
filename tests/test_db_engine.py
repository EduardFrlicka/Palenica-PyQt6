"""The db layer must signal failure without touching the GUI.

These import the SQLAlchemy/libsql stack, so they are skipped where it is not
installed - notably the CI 'test' job, which installs only pytest+requests.
They run anywhere the app's runtime dependencies are present.
"""

import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("libsql")

import config as config_mod
import db
from db import db_engine
from db.errors import DatabaseUnavailable, DatabaseConfigError, DatabaseOffline


def test_error_hierarchy_carries_user_message():
    err = DatabaseConfigError("boom")
    assert isinstance(err, DatabaseUnavailable)
    assert err.user_message == "boom"
    assert isinstance(DatabaseOffline("x"), DatabaseUnavailable)


def test_db_layer_has_no_gui_imports():
    # The decoupling in one assertion: db_engine no longer pulls in the dialog
    # helpers it used to call, so `import db` stays Qt-free and headless-safe.
    assert not hasattr(db_engine, "alert")
    assert not hasattr(db_engine, "error")


def test_engine_init_raises_when_url_missing(monkeypatch):
    monkeypatch.setitem(config_mod.config.config, "database", {"url": ""})
    with pytest.raises(DatabaseConfigError):
        db_engine.engine_init()


def test_engine_init_raises_when_no_database_section(monkeypatch):
    monkeypatch.delitem(config_mod.config.config, "database", raising=False)
    with pytest.raises(DatabaseConfigError):
        db_engine.engine_init()


def test_get_engine_attempts_once_and_caches_the_failure(monkeypatch):
    # Start from a clean module state.
    monkeypatch.setattr(db_engine, "engine", None)
    monkeypatch.setattr(db_engine, "_init_attempted", False)
    monkeypatch.setattr(db_engine, "_init_error", None)

    calls = []

    def boom():
        calls.append(1)
        raise DatabaseOffline("offline")

    monkeypatch.setattr(db_engine, "engine_init", boom)

    assert db_engine.get_engine() is None
    assert db_engine.get_engine() is None  # a second check must not reconnect
    assert len(calls) == 1  # ... so engine_init ran exactly once

    error = db_engine.get_engine_error()
    assert isinstance(error, DatabaseOffline)
    assert error.user_message == "offline"
