from __future__ import annotations

import json
from typing import Any

from app.db.database import Database


class ConversationRepository:
    """
    High-level persistence API for transcripts and decisions.
    """

    def __init__(self, db: Database):
        self.db = db
        self.db.initialize()

    def save_transcript(self, text: str, language: str | None = None) -> int:
        query = "INSERT INTO transcripts(text, language) VALUES (?, ?)"
        params = (text, language)
        with self.db.connect() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return int(cursor.lastrowid)

    def save_decision(self, transcript_id: int, intent: str, payload: dict[str, Any]) -> int:
        query = "INSERT INTO decisions(transcript_id, intent, payload) VALUES (?, ?, ?)"
        params = (transcript_id, intent, json.dumps(payload, ensure_ascii=False))
        with self.db.connect() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return int(cursor.lastrowid)

    def save_car_event(self, plate: str, source: str | None = None) -> int:
        query = "INSERT INTO car_events(plate, source) VALUES (?, ?)"
        params = (plate, source)
        with self.db.connect() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return int(cursor.lastrowid)

    def list_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        query = """
        SELECT t.id as transcript_id,
               t.created_at as transcript_created_at,
               t.language,
               t.text,
               d.intent,
               d.payload,
               d.created_at as decision_created_at
        FROM transcripts t
        LEFT JOIN decisions d ON t.id = d.transcript_id
        ORDER BY t.id DESC
        LIMIT ?
        """
        rows = self.db.fetchall(query, (limit,))
        return [dict(row) for row in rows]

    def seed_sample_data(self) -> None:
        """
        Insert a couple of sample transcripts/decisions to simplify local testing.
        Safe to call multiple times.
        """
        existing = self.db.fetchall("SELECT COUNT(*) as cnt FROM transcripts")
        if existing and existing[0]["cnt"] > 0:
            return

        t1 = self.save_transcript("открой шлагбаум", language="ru")
        self.save_decision(
            t1,
            "open_gate",
            {"intent": "open_gate", "action": "say", "payload": {"device": "gate", "command": "open"}},
        )

        t2 = self.save_transcript("need a ticket", language="en")
        self.save_decision(
            t2,
            "issue_ticket",
            {"intent": "issue_ticket", "action": "say", "payload": {"device": "ticket_machine", "command": "issue"}},
        )

    def seed_history_sample(self) -> None:
        """
        Populate HISTORY with a couple of demo rows if empty.
        """
        rows = self.db.fetchall("SELECT COUNT(*) as cnt FROM HISTORY")
        if rows and rows[0]["cnt"] > 0:
            return

        entries = [
            {
                "N_PAR": 1,
                "BE_N_NUMTIT": "TICKET-001",
                "BE_D_DATTRA": "2025-01-01T10:00:00",
                "BE_N_EQU": 3,
                "NB_TOTPAI": 1,
                "N_CNTPRI": "CNT-100",
                "T_FAMTIT": 1,
                "BE_N_LICPLA": "ABC123",
                "BS_D_DATTRA": "2025-01-01T12:30:00",
                "BS_N_LICPLA": "ABC123",
                "TXT_COMMENT": "Demo entry/exit",
            },
            {
                "N_PAR": 2,
                "BE_N_NUMTIT": "TICKET-002",
                "BE_D_DATTRA": "2025-02-10T09:15:00",
                "BE_N_EQU": 2,
                "NB_TOTPAI": 1,
                "N_CNTPRI": "CNT-200",
                "T_FAMTIT": 1,
                "BE_N_LICPLA": "XYZ789",
                "BS_D_DATTRA": None,
                "BS_N_LICPLA": None,
                "TXT_COMMENT": "In parking, exit pending",
            },
        ]

        cols = entries[0].keys()
        placeholders = ", ".join(["?" for _ in cols])
        col_names = ", ".join(cols)
        query = f"INSERT INTO HISTORY ({col_names}) VALUES ({placeholders})"

        with self.db.connect() as conn:
            for row in entries:
                conn.execute(query, tuple(row.values()))
            conn.commit()

    def find_history_by_plate(self, plate: str) -> list[dict[str, Any]]:
        """
        Find HISTORY records where plate matches entry/exit/alternate plate fields (case-insensitive).
        """
        normalized = plate.strip().upper()
        query = """
        SELECT * FROM HISTORY
        WHERE UPPER(BE_N_LICPLA) = ?
           OR UPPER(BS_N_LICPLA) = ?
           OR UPPER(BE_N_LICPLA_CR) = ?
           OR UPPER(BS_N_LICPLA_CR) = ?
           OR UPPER(N_LICPLA_BIS) = ?
        """
        rows = self.db.fetchall(
            query, (normalized, normalized, normalized, normalized, normalized)
        )
        return [dict(row) for row in rows]
