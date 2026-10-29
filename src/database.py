import sqlite3
from datetime import datetime, timezone


DB_PATH = "pipeline_health.db"


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Return a connection to the SQLite database."""
    return sqlite3.connect(db_path)


def init_db(db_path: str = DB_PATH) -> None:
    """Create the health_checks table if it does not already exist."""
    with get_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS health_checks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                check_name  TEXT    NOT NULL,
                status      TEXT    NOT NULL,
                details     TEXT,
                run_at      TEXT    NOT NULL
            )
        """)
        conn.commit()


def insert_result(check_name: str, status: str, details: str,
                  db_path: str = DB_PATH) -> None:
    """Persist a single health-check result."""
    run_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with get_connection(db_path) as conn:
        conn.execute(
            "INSERT INTO health_checks (check_name, status, details, run_at) "
            "VALUES (?, ?, ?, ?)",
            (check_name, status, details, run_at),
        )
        conn.commit()


def get_all_results(db_path: str = DB_PATH) -> list[dict]:
    """Return all stored health-check results as a list of dicts."""
    with get_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM health_checks ORDER BY run_at DESC"
        ).fetchall()
    return [dict(row) for row in rows]
