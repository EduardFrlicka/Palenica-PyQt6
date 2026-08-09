"""Create the database schema from the SQLAlchemy models.

Reads [database].url from config.toml and issues CREATE TABLE for every model
registered on db.Base.metadata. Existing tables are left untouched, and the
only rows inserted are the production lines listed in PRODUCTION_LINES, which
are skipped if they already exist, so this is safe to re-run.

Usage (from the repository root):
    python3 src/create_tables.py
"""

import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session
import config
import db

PRODUCTION_LINES = ("A", "B")


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

    with Session(engine) as session:
        existing = {
            line.name
            for line in session.query(db.ProductionLine)
            .filter(db.ProductionLine.name.in_(PRODUCTION_LINES))
            .all()
        }

        for name in PRODUCTION_LINES:
            if name in existing:
                print(f"{'exists':8} production line {name}")
                continue
            session.add(db.ProductionLine(name))
            print(f"{'created':8} production line {name}")

        session.commit()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
