import sqlite3
from app.config.settings import settings

def _init_tables(conn: sqlite3.Connection):
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            description TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role_id INTEGER NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (role_id) REFERENCES roles (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            client_phone TEXT NOT NULL,
            direction TEXT NOT NULL,      -- "INBOUND" o "OUTBOUND"
            status TEXT NOT NULL,         -- "QUEUED", "PROCESSING", "DONE", "ERROR"
            is_sale INTEGER DEFAULT 0,
            start_time TEXT,
            end_time TEXT,
            audio_file_url TEXT,
            resumen_ai TEXT,
            created_at TEXT,
            FOREIGN KEY (agent_id) REFERENCES usuarios (id)
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM roles")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO roles VALUES (?, ?, ?)", [
            (1, 'LEARNER', 'Learner user'),
            (2, 'SUPERVISOR', 'Supervisor user'),
            (3, 'ADMIN', 'Administrator user')
        ])

    conn.commit()

def get_db():
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    _init_tables(conn)
    try:
        yield conn
    finally:
        conn.close()
