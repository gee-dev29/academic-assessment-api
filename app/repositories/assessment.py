import sqlite3
from typing import Any


def subject_exists(connection: sqlite3.Connection, subject_id: int) -> bool:
    if subject_id <= 0:
        return False
    row = connection.execute(
        "SELECT 1 FROM subjects WHERE id = ?", (subject_id,)
    ).fetchone()
    return row is not None


def create_assessment(
    connection: sqlite3.Connection, subject_id: int, name: str, max_score: float
) -> dict[str, Any]:
    if subject_id <= 0:
        raise ValueError("Subject ID must be greater than zero")
    normalized_name = name.strip()
    if not normalized_name:
        raise ValueError("Assessment name must not be blank")
    if max_score <= 0:
        raise ValueError("Maximum score must be greater than zero")

    cursor = connection.execute(
        "INSERT INTO assessments (subject_id, name, max_score) VALUES (?, ?, ?)",
        (subject_id, normalized_name, max_score),
    )
    assessment_id = cursor.lastrowid
    if assessment_id is None:
        raise RuntimeError("Creating an assessment did not return an ID")
    connection.commit()
    return {
        "id": assessment_id,
        "subject_id": subject_id,
        "name": normalized_name,
        "max_score": max_score,
    }


def list_assessments(
    connection: sqlite3.Connection, subject_id: int | None
) -> list[dict[str, Any]]:
    if subject_id is None:
        rows = connection.execute(
            "SELECT id, subject_id, name, max_score FROM assessments ORDER BY id"
        ).fetchall()
    else:
        rows = connection.execute(
            """
            SELECT id, subject_id, name, max_score
            FROM assessments WHERE subject_id = ? ORDER BY id
            """,
            (subject_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_assessment(
    connection: sqlite3.Connection, assessment_id: int
) -> dict[str, Any] | None:
    row = connection.execute(
        "SELECT id, subject_id, name, max_score FROM assessments WHERE id = ?",
        (assessment_id,),
    ).fetchone()
    return dict(row) if row is not None else None
