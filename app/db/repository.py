from __future__ import annotations

import json
from typing import Any

from app.db.database import Database


class ConversationRepository:
    
    #igh-level persistence API for transcripts and decisions.
    

    def __init__(self, db: Database):
        #Initialize repository and ensure schema exists.
        self.db = db
        self.db.initialize()

    def save_transcript(self, text: str, language: str | None = None) -> int:
        #Insert a transcript row and return its id.
        query = "INSERT INTO transcripts(text, language) VALUES (?, ?)"
        params = (text, language)
        with self.db.connect() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return int(cursor.lastrowid)

    def save_decision(self, transcript_id: int, intent: str, payload: dict[str, Any]) -> int:
        #Insert a decision linked to a transcript and return its id.
        query = "INSERT INTO decisions(transcript_id, intent, payload) VALUES (?, ?, ?)"
        params = (transcript_id, intent, json.dumps(payload, ensure_ascii=False))
        with self.db.connect() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return int(cursor.lastrowid)

    def save_car_event(self, plate: str, source: str | None = None) -> int:
        #Insert a camera event and return its id.
        query = "INSERT INTO car_events(plate, source) VALUES (?, ?)"
        params = (plate, source)
        with self.db.connect() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return int(cursor.lastrowid)

    def list_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        #Return latest transcripts with decisions joined.
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

    # Seeding sample transcripts and decisions
    def seed_sample_data(self) -> None:
        #Insert a couple of sample transcripts/decisions to simplify local testing.
        #Safe to call multiple times.
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

    # Seeding HISTORY with sample data
    def seed_history_sample(self) -> None:
    #Populate HISTORY with a couple of demo rows if empty.

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

    #Find HISTORY records where plate matches entry/exit/alternate plate fields (case-insensitive).

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

    def find_history_by_ticket(self, ticket_number: str) -> list[dict[str, Any]]:
    #Find HISTORY rows by ticket/pass number (exact match)."""
        rows = self.db.fetchall("SELECT * FROM HISTORY WHERE BE_N_NUMTIT = ?", (ticket_number,))
        return [dict(row) for row in rows]

    def find_history_debts_by_plate(self, plate: str) -> list[dict[str, Any]]:
    #Find HISTORY rows for a plate where есть долг (MT_TELBAD > 0).
    #Note: поле T_MONTANT в описании соответствует MT_TELBAD в схеме.

        normalized = plate.strip().upper()
        query = """
        SELECT * FROM HISTORY
        WHERE MT_TELBAD IS NOT NULL
          AND MT_TELBAD > 0
          AND (
                UPPER(BE_N_LICPLA) = ?
             OR UPPER(BS_N_LICPLA) = ?
             OR UPPER(BE_N_LICPLA_CR) = ?
             OR UPPER(BS_N_LICPLA_CR) = ?
             OR UPPER(N_LICPLA_BIS) = ?
          )
        """
        rows = self.db.fetchall(
            query, (normalized, normalized, normalized, normalized, normalized)
        )
        return [dict(row) for row in rows]

    def has_no_debt(self, plate: str) -> bool:
        #Convenience: True если по номеру нет записей с MT_TELBAD > 0.
        return len(self.find_history_debts_by_plate(plate)) == 0

    def get_history_by_id(self, history_id: int) -> dict[str, Any] | None:
        #Fetch a single HISTORY record by its primary key.
        rows = self.db.fetchall("SELECT * FROM HISTORY WHERE ID_HISTORY = ?", (history_id,))
        return dict(rows[0]) if rows else None

    def list_history_recent(self, limit: int = 50) -> list[dict[str, Any]]:
        #Return latest HISTORY rows.
        rows = self.db.fetchall("SELECT * FROM HISTORY ORDER BY ID_HISTORY DESC LIMIT ?", (limit,))
        return [dict(row) for row in rows]

    def search_history_by_entry_date(
        self, date_from: str | None = None, date_to: str | None = None
    ) -> list[dict[str, Any]]:
        #Filter HISTORY by entry datetime range (BE_D_DATTRA).
        #Dates are ISO-like strings; None leaves the boundary open.
        clauses = []
        params: list[Any] = []
        if date_from:
            clauses.append("BE_D_DATTRA >= ?")
            params.append(date_from)
        if date_to:
            clauses.append("BE_D_DATTRA <= ?")
            params.append(date_to)
        where = " AND ".join(clauses) if clauses else "1=1"
        query = f"SELECT * FROM HISTORY WHERE {where} ORDER BY BE_D_DATTRA DESC"
        rows = self.db.fetchall(query, params)
        return [dict(row) for row in rows]

    def list_car_events(self, limit: int = 100) -> list[dict[str, Any]]:
        #Return recent car_events rows.
        rows = self.db.fetchall("SELECT * FROM car_events ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(row) for row in rows]

    def find_car_events_by_plate(self, plate: str) -> list[dict[str, Any]]:
        #Find car_events rows by plate.
        rows = self.db.fetchall("SELECT * FROM car_events WHERE plate = ? ORDER BY id DESC", (plate,))
        return [dict(row) for row in rows]

    def search_transcripts(self, text_like: str, limit: int = 50) -> list[dict[str, Any]]:
        #Find transcripts containing a substring (case-insensitive).
        pattern = f"%{text_like}%"
        rows = self.db.fetchall(
            "SELECT * FROM transcripts WHERE LOWER(text) LIKE LOWER(?) ORDER BY id DESC LIMIT ?",
            (pattern, limit),
        )
        return [dict(row) for row in rows]

    def get_decisions_for_transcript(self, transcript_id: int) -> list[dict[str, Any]]:
        #Return all decisions associated with a transcript.
        rows = self.db.fetchall(
            "SELECT * FROM decisions WHERE transcript_id = ? ORDER BY id DESC", (transcript_id,)
        )
        return [dict(row) for row in rows]
