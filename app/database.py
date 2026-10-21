import os
import sqlite3
from pathlib import Path
from typing import Generator


DATABASE_PATH = os.getenv("DATABASE_PATH", "data/scores.db")


def get_connection() -> Generator[sqlite3.Connection, None, None]:
    if DATABASE_PATH != ":memory:":
        Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
    finally:
        connection.close()


def create_tables() -> None:
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER NOT NULL REFERENCES subjects(id),
                name TEXT NOT NULL,
                max_score REAL NOT NULL CHECK (max_score > 0),
                UNIQUE (subject_id, name)
            );

            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assessment_id INTEGER NOT NULL REFERENCES assessments(id),
                student_id TEXT NOT NULL,
                score REAL NOT NULL CHECK (score >= 0),
                UNIQUE (assessment_id, student_id)
            );
            """
        )
        connection.commit()
    finally:
        connection.close()
