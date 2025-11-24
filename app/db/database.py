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

                CREATE TABLE IF NOT EXISTS HISTORY (
                    ID_HISTORY INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    N_PAR INTEGER NOT NULL,
                    BE_N_NUMTIT TEXT NOT NULL,
                    BE_D_DATTRA DATETIME NOT NULL,
                    BE_N_EQU INTEGER NOT NULL,
                    BE_N_CAT INTEGER,
                    BE_N_LICPLA TEXT,
                    NOM_BE_IMG TEXT,
                    BE_IMG BLOB,
                    BE_F_ERR INTEGER,
                    BS_D_DATTRA DATETIME,
                    BS_N_EQU INTEGER,
                    BS_N_CAT INTEGER,
                    BS_N_LICPLA TEXT,
                    DH_LIMSOR DATETIME,
                    NOM_BS_IMG TEXT,
                    BS_IMG BLOB,
                    BS_F_ERR INTEGER,
                    NB_TOTPAI INTEGER NOT NULL,
                    DHMP DATETIME,
                    N_NUMTAR INTEGER,
                    MT_PMTESPMT1 NUMERIC,
                    MT_PMTCHQBANMT1 NUMERIC,
                    MT_PMTCARBANMT1 NUMERIC,
                    MT_PMTCARDECMT1 NUMERIC,
                    MT_PORMON NUMERIC,
                    MT_PMTFACMT1 NUMERIC,
                    MT_TOTREDMT1 NUMERIC,
                    N_CAT INTEGER,
                    N_CNTPRI TEXT NOT NULL,
                    T_FAMTIT INTEGER NOT NULL,
                    N_ZONSTA INTEGER,
                    T_FRA INTEGER,
                    TXT_COMMENT TEXT,
                    MT_TELBAD NUMERIC,
                    BE_N_LICPLA_CR TEXT,
                    BS_N_LICPLA_CR TEXT,
                    N_LICPLA_BIS TEXT,
                    DIGIT_CLI_ID TEXT,
                    DIGIT_BE_TYP_IDENT INTEGER,
                    DIGIT_BE_NUM_IDENT TEXT,
                    DIGIT_BS_TYP_IDENT INTEGER,
                    DIGIT_BS_NUM_IDENT TEXT,
                    N_CBESPANCRY TEXT,
                    N_TYPCBESCRY INTEGER,
                    BIN TEXT,
                    EXPIRE TEXT,
                    CLASSENRJ TEXT,
                    ENTRY_NOTIFY_STATUS INTEGER,
                    EXIT_NOTIFY_STATUS INTEGER
                );
                """
            )
            conn.commit()
