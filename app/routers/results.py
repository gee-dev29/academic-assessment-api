import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.database import get_connection
from app.exceptions import (
    AssessmentNotFoundError,
    DuplicateScoreError,
    ScoreExceedsMaximumError,
    ScoreNotFoundError,
    StudentResultsNotFoundError,
)
from app.repositories.assessment import get_assessment
from app.repositories.result import (
    create_score,
    get_score_details,
    get_student_average,
    get_student_results,
    update_score,
)
from app.schemas.result import (
    AverageResponse,
    ResultResponse,
    ScoreCreate,
    ScoreCreated,
    ScoreUpdate,
)
from app.security import require_auth


router = APIRouter(
    tags=["student results"],
    dependencies=[Depends(require_auth)],
)
Connection = Annotated[sqlite3.Connection, Depends(get_connection)]


@router.post(
    "/scores", response_model=ScoreCreated, status_code=status.HTTP_201_CREATED
)
def add_score(score: ScoreCreate, connection: Connection) -> dict[str, int | str]:
    assessment = get_assessment(connection, score.assessment_id)
    if assessment is None:
        raise AssessmentNotFoundError()
    if score.score > assessment["max_score"]:
        raise ScoreExceedsMaximumError(assessment["max_score"])

    try:
        score_id = create_score(
            connection, score.assessment_id, score.student_id, score.score
        )
    except sqlite3.IntegrityError as error:
        raise DuplicateScoreError() from error
    return {"id": score_id, "message": "Score added"}


@router.put("/scores/{score_id}", response_model=ResultResponse)
def change_score(
    score_id: int, update: ScoreUpdate, connection: Connection
) -> dict:
    row = get_score_details(connection, score_id)
    if row is None:
        raise ScoreNotFoundError()
    if update.score > row["max_score"]:
        raise ScoreExceedsMaximumError(row["max_score"])

    if not update_score(connection, score_id, update.score):
        raise ScoreNotFoundError()
    return {
        "assessment_id": row["assessment_id"],
        "assessment_name": row["assessment_name"],
        "subject_name": row["subject_name"],
        "score": update.score,
        "max_score": row["max_score"],
        "percentage": round(update.score * 100 / row["max_score"], 2),
    }


@router.get(
    "/students/{student_id}/results", response_model=list[ResultResponse]
)
def student_results(student_id: str, connection: Connection) -> list[dict]:
    return get_student_results(connection, student_id.strip())


@router.get(
    "/students/{student_id}/average", response_model=AverageResponse
)
def student_average(student_id: str, connection: Connection) -> dict:
    normalized_student_id = student_id.strip()
    average = get_student_average(connection, normalized_student_id)
    if average is None:
        raise StudentResultsNotFoundError()
    return average
