"""Create the database schema from the SQLAlchemy models.

Reads [database].url from config.toml and issues CREATE TABLE for every model
registered on db.Base.metadata. Schema only - no rows are inserted. Existing
tables are left untouched, so this is safe to re-run.

Usage (from the repository root):
    python3 src/create_tables.py
"""

import sys
from sqlalchemy import create_engine, inspect
import config
import db


def main() -> int:
    url = config.config.get("database", "url")
    if not url:
        print("No [database].url found in config.toml", file=sys.stderr)
        return 1

    engine = create_engine(url, pool_pre_ping=True)

    before = set(inspect(engine).get_table_names())
    db.Base.metadata.create_all(engine)
    after = set(inspect(engine).get_table_names())

    for name in sorted(db.Base.metadata.tables):
        print(f"{'created' if name in after - before else 'exists':8} {name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
