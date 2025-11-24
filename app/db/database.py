from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, Optional


class Database:
    """
    Thin wrapper around SQLite to keep connection options in one place.
    """

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        """
        Return a connection configured for row access by column name.
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def execute(self, query: str, params: Iterable = ()) -> None:
        with self.connect() as conn:
            conn.execute(query, tuple(params))
            conn.commit()

    def fetchall(self, query: str, params: Iterable = ()) -> list[sqlite3.Row]:
        with self.connect() as conn:
            cursor = conn.execute(query, tuple(params))
            return cursor.fetchall()

    def initialize(self) -> None:
        """
        Idempotent schema initialization.
        """
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS transcripts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    language TEXT,
                    text TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transcript_id INTEGER NOT NULL,
                    intent TEXT,
                    payload TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (transcript_id) REFERENCES transcripts(id)
                );

                CREATE TABLE IF NOT EXISTS car_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plate TEXT NOT NULL,
                    source TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            conn.commit()
