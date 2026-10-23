from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_tables
from app.routers import assessments, results, subjects


create_tables()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    create_tables()
    yield


app = FastAPI(
    title="Student Results API",
    description="A small API for subjects, assessments, and student scores.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(subjects.router)
app.include_router(assessments.router)
app.include_router(results.router)
