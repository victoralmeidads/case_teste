import sqlite3
from pathlib import Path


def record_ingestion(database_path: Path, source: str, input_rows: int, accepted_rows: int, issue_count: int, status: str) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS ingestion_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                executed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                source TEXT NOT NULL,
                input_rows INTEGER NOT NULL,
                accepted_rows INTEGER NOT NULL,
                issue_count INTEGER NOT NULL,
                status TEXT NOT NULL
            )"""
        )
        connection.execute(
            "INSERT INTO ingestion_audit(source, input_rows, accepted_rows, issue_count, status) VALUES (?, ?, ?, ?, ?)",
            (source, input_rows, accepted_rows, issue_count, status),
        )


def read_recent_audits(database_path: Path, limit: int = 20):
    if not database_path.exists():
        return []
    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT executed_at, source, input_rows, accepted_rows, issue_count, status FROM ingestion_audit ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]