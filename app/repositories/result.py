import sqlite3
from typing import Any


def create_score(
    connection: sqlite3.Connection, assessment_id: int, student_id: str, score: float
) -> int:
    normalized_student_id = student_id.strip()
    if assessment_id <= 0:
        raise ValueError("Assessment ID must be greater than zero")
    if not normalized_student_id:
        raise ValueError("Student ID must not be blank")
    if score < 0:
        raise ValueError("Score must not be negative")

    cursor = connection.execute(
        """
        INSERT INTO scores (assessment_id, student_id, score)
        VALUES (?, ?, ?)
        """,
        (assessment_id, normalized_student_id, score),
    )
    score_id = cursor.lastrowid
    if score_id is None:
        raise RuntimeError("Creating a score did not return an ID")
    connection.commit()
    return score_id


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
