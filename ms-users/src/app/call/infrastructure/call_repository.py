import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

class CallRepository:
    def __init__(self, db_conn: sqlite3.Connection):
        self.db = db_conn
        self.db.row_factory = sqlite3.Row

    # =====================
    # CREATE
    # =====================
    def create_call(self, agent_id: int, client_phone: str,
                    direction: str, status: str = "QUEUED",
                    is_sale: bool = False, start_time: str = None) -> Dict[str, Any]:
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO calls (
                agent_id, client_phone, direction, status,
                is_sale, start_time, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            agent_id, client_phone, direction, status,
            1 if is_sale else 0,
            start_time or datetime.now(timezone.utc).isoformat(),
            datetime.now(timezone.utc).isoformat()
        ))
        self.db.commit()

        call_id = cursor.lastrowid
        return self.get_call_by_id(call_id)

    # =====================
    # READ
    # =====================
    def get_call_by_id(self, call_id: int) -> Optional[Dict[str, Any]]:
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT c.*, u.first_name || ' ' || u.last_name AS agent_name
            FROM calls c
            LEFT JOIN usuarios u ON c.agent_id = u.id
            WHERE c.id = ?
        """, (call_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_calls(self, skip: int = 0, limit: int = 100,
                      direction: Optional[str] = None,
                      status: Optional[str] = None,
                      agent_id: Optional[int] = None) -> List[Dict[str, Any]]:
        cursor = self.db.cursor()
        query = """
            SELECT c.*, u.first_name || ' ' || u.last_name AS agent_name
            FROM calls c
            LEFT JOIN usuarios u ON c.agent_id = u.id
            WHERE 1=1
        """
        params = []

        if direction is not None:
            query += " AND c.direction = ?"
            params.append(direction)

        if status is not None:
            query += " AND c.status = ?"
            params.append(status)

        if agent_id is not None:
            query += " AND c.agent_id = ?"
            params.append(agent_id)

        query += " ORDER BY c.created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def count_calls(self, direction: Optional[str] = None,
                    status: Optional[str] = None,
                    agent_id: Optional[int] = None) -> int:
        cursor = self.db.cursor()
        query = "SELECT COUNT(*) FROM calls WHERE 1=1"
        params = []

        if direction is not None:
            query += " AND direction = ?"
            params.append(direction)

        if status is not None:
            query += " AND status = ?"
            params.append(status)

        if agent_id is not None:
            query += " AND agent_id = ?"
            params.append(agent_id)

        cursor.execute(query, params)
        return cursor.fetchone()[0]

    # =====================
    # UPDATE
    # =====================
    def update_call(self, call: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        cursor = self.db.cursor()
        set_clause = []
        params = []

        for key, value in kwargs.items():
            if value is not None and key in [
                "client_phone", "status", "is_sale", "start_time",
                "end_time", "audio_file_url", "resumen_ai"
            ]:
                set_clause.append(f"{key} = ?")
                params.append(value)

        if set_clause:
            set_clause.append("updated_at = ?")
            params.append(datetime.now(timezone.utc).isoformat())
            params.append(call["id"])

            query = f"UPDATE calls SET {', '.join(set_clause)} WHERE id = ?"
            cursor.execute(query, params)
            self.db.commit()

        return self.get_call_by_id(call["id"])

    # =====================
    # DELETE
    # =====================
    def delete_call(self, call_id: int) -> None:
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM calls WHERE id = ?", (call_id,))
        self.db.commit()
