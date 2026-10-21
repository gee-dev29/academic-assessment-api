import sqlite3
from typing import Any


def create_subject(connection: sqlite3.Connection, name: str) -> dict[str, Any]:
    cursor = connection.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
    connection.commit()
    return {"id": cursor.lastrowid, "name": name}


def list_subjects(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT id, name FROM subjects ORDER BY name"
    ).fetchall()
    return [dict(row) for row in rows]


def subject_exists(connection: sqlite3.Connection, subject_id: int) -> bool:
    row = connection.execute(
        "SELECT 1 FROM subjects WHERE id = ?", (subject_id,)
    ).fetchone()
    return row is not None


def create_assessment(
    connection: sqlite3.Connection, subject_id: int, name: str, max_score: float
) -> dict[str, Any]:
    cursor = connection.execute(
        "INSERT INTO assessments (subject_id, name, max_score) VALUES (?, ?, ?)",
        (subject_id, name, max_score),
    )
    connection.commit()
    return {
        "id": cursor.lastrowid,
        "subject_id": subject_id,
        "name": name,
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


def create_score(
    connection: sqlite3.Connection, assessment_id: int, student_id: str, score: float
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO scores (assessment_id, student_id, score)
        VALUES (?, ?, ?)
        """,
        (assessment_id, student_id, score),
    )
    connection.commit()
    return cursor.lastrowid


def get_score_details(
    connection: sqlite3.Connection, score_id: int
) -> dict[str, Any] | None:
    row = connection.execute(
        """
        SELECT
            scores.assessment_id,
            assessments.max_score,
            assessments.name AS assessment_name,
            subjects.name AS subject_name
        FROM scores
        JOIN assessments ON assessments.id = scores.assessment_id
        JOIN subjects ON subjects.id = assessments.subject_id
        WHERE scores.id = ?
        """,
        (score_id,),
    ).fetchone()
    return dict(row) if row is not None else None


def update_score(
    connection: sqlite3.Connection, score_id: int, score: float
) -> bool:
    cursor = connection.execute(
        "UPDATE scores SET score = ? WHERE id = ?", (score, score_id)
    )
    connection.commit()
    return cursor.rowcount > 0


def get_student_results(
    connection: sqlite3.Connection, student_id: str
) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT
            assessments.id AS assessment_id,
            assessments.name AS assessment_name,
            subjects.name AS subject_name,
            scores.score AS score,
            assessments.max_score AS max_score,
            ROUND(scores.score * 100.0 / assessments.max_score, 2) AS percentage
        FROM scores
        JOIN assessments ON assessments.id = scores.assessment_id
        JOIN subjects ON subjects.id = assessments.subject_id
        WHERE scores.student_id = ?
        ORDER BY subjects.name, assessments.name
        """,
        (student_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def get_student_average(
    connection: sqlite3.Connection, student_id: str
) -> dict[str, Any] | None:
    row = connection.execute(
        """
        SELECT
            ROUND(AVG(scores.score * 100.0 / assessments.max_score), 2)
                AS average_percentage,
            COUNT(*) AS assessment_count
        FROM scores
        JOIN assessments ON assessments.id = scores.assessment_id
        WHERE scores.student_id = ?
        """,
        (student_id,),
    ).fetchone()
    if row is None or row["assessment_count"] == 0:
        return None
    return {
        "student_id": student_id,
        "average_percentage": row["average_percentage"],
        "assessment_count": row["assessment_count"],
    }
