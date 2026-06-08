"""SQLAlchemy engine and schema bootstrap."""

from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from .config import DATABASE_URL

_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=5)
    return _engine


def init_db() -> None:
    """Create tables and seed demo rows if empty."""
    eng = get_engine()
    with eng.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS items (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL
                );
                """
            )
        )
        row = conn.execute(text("SELECT COUNT(*) AS c FROM items")).mappings().first()
        if row and int(row["c"]) == 0:
            conn.execute(text("INSERT INTO items (name) VALUES ('widget'), ('gadget'), ('sprocket')"))
