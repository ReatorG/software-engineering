import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserRepository:
    def __init__(self, db_conn: sqlite3.Connection):
        self.db = db_conn
        self.db.row_factory = sqlite3.Row

    def create_user(self, first_name: str, last_name: str, email: str,
                   password: str, role_id: int) -> Dict[str, Any]:
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO usuarios (first_name, last_name, email, password, role_id, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, 1, ?)
        """, (first_name, last_name, email, password, role_id, datetime.now().isoformat()))
        self.db.commit()

        user_id = cursor.lastrowid
        return self.get_user_by_id(user_id)

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT u.*, r.name as role_name, r.description as role_description
            FROM usuarios u
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE u.id = ?
        """, (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT u.*, r.name as role_name, r.description as role_description
            FROM usuarios u
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE u.email = ?
        """, (email,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_users(self, skip: int = 0, limit: int = 100,
                     role_id: Optional[int] = None,
                     is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        cursor = self.db.cursor()
        query = """
            SELECT u.*, r.name as role_name, r.description as role_description
            FROM usuarios u
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE 1=1
        """
        params = []

        if role_id is not None:
            query += " AND u.role_id = ?"
            params.append(role_id)

        if is_active is not None:
            query += " AND u.is_active = ?"
            params.append(1 if is_active else 0)

        query += " LIMIT ? OFFSET ?"
        params.extend([limit, skip])

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def count_users(self, role_id: Optional[int] = None,
                   is_active: Optional[bool] = None) -> int:
        cursor = self.db.cursor()
        query = "SELECT COUNT(*) FROM usuarios WHERE 1=1"
        params = []

        if role_id is not None:
            query += " AND role_id = ?"
            params.append(role_id)

        if is_active is not None:
            query += " AND is_active = ?"
            params.append(1 if is_active else 0)

        cursor.execute(query, params)
        return cursor.fetchone()[0]

    def update_user(self, user: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        cursor = self.db.cursor()
        set_clause = []
        params = []

        for key, value in kwargs.items():
            if value is not None and key in ['first_name', 'last_name', 'email']:
                set_clause.append(f"{key} = ?")
                params.append(value)

        if set_clause:
            set_clause.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(user['id'])

            query = f"UPDATE usuarios SET {', '.join(set_clause)} WHERE id = ?"
            cursor.execute(query, params)
            self.db.commit()

        return self.get_user_by_id(user['id'])

    def update_user_role(self, user: Dict[str, Any], role_id: int) -> Dict[str, Any]:
        cursor = self.db.cursor()
        cursor.execute("""
            UPDATE usuarios SET role_id = ?, updated_at = ?
            WHERE id = ?
        """, (role_id, datetime.now().isoformat(), user['id']))
        self.db.commit()
        return self.get_user_by_id(user['id'])

    def disable_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        cursor = self.db.cursor()
        cursor.execute("""
            UPDATE usuarios SET is_active = 0, updated_at = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), user['id']))
        self.db.commit()
        return self.get_user_by_id(user['id'])

    def enable_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        cursor = self.db.cursor()
        cursor.execute("""
            UPDATE usuarios SET is_active = 1, updated_at = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), user['id']))
        self.db.commit()
        return self.get_user_by_id(user['id'])

    def get_role_by_id(self, role_id: int) -> Optional[Dict[str, Any]]:
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM roles WHERE id = ?", (role_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
