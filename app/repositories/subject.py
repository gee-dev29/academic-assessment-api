import sqlite3
from typing import Any


def create_subject(connection: sqlite3.Connection, name: str) -> dict[str, Any]:
    normalized_name = name.strip()
    if not normalized_name:
        raise ValueError("Subject name must not be blank")

    cursor = connection.execute(
        "INSERT INTO subjects (name) VALUES (?)", (normalized_name,)
    )
    subject_id = cursor.lastrowid
    if subject_id is None:
        raise RuntimeError("Creating a subject did not return an ID")
    connection.commit()
    return {"id": subject_id, "name": normalized_name}


def list_subjects(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT id, name FROM subjects ORDER BY name"
    ).fetchall()
    return [dict(row) for row in rows]
