import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_connection
from app.repository import create_subject, list_subjects
from app.schemas import SubjectCreate, SubjectResponse
from app.security import require_auth


router = APIRouter(
    prefix="/subjects",
    tags=["subjects"],
    dependencies=[Depends(require_auth)],
)
Connection = Annotated[sqlite3.Connection, Depends(get_connection)]


@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def add_subject(subject: SubjectCreate, connection: Connection) -> dict:
    try:
        return create_subject(connection, subject.name)
    except sqlite3.IntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A subject with this name already exists",
        ) from error


@router.get("", response_model=list[SubjectResponse])
def get_subjects(connection: Connection) -> list[dict]:
    return list_subjects(connection)
