import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.database import get_connection
from app.repository import create_assessment, list_assessments, subject_exists
from app.schemas import AssessmentCreate, AssessmentResponse
from app.security import require_auth


router = APIRouter(
    prefix="/assessments",
    tags=["assessments"],
    dependencies=[Depends(require_auth)],
)
Connection = Annotated[sqlite3.Connection, Depends(get_connection)]


@router.post(
    "", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED
)
def add_assessment(assessment: AssessmentCreate, connection: Connection) -> dict:
    if not subject_exists(connection, assessment.subject_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found"
        )
    try:
        return create_assessment(
            connection,
            assessment.subject_id,
            assessment.name,
            assessment.max_score,
        )
    except sqlite3.IntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An assessment with this name already exists for the subject",
        ) from error


@router.get("", response_model=list[AssessmentResponse])
def get_assessments(
    connection: Connection, subject_id: Annotated[int | None, Query(gt=0)] = None
) -> list[dict]:
    return list_assessments(connection, subject_id)
