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
