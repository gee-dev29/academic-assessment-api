from pydantic import BaseModel, Field, field_validator


class ScoreCreate(BaseModel):
    assessment_id: int = Field(gt=0)
    student_id: str = Field(min_length=1, max_length=50)
    score: float = Field(ge=0, allow_inf_nan=False)

    @field_validator("student_id")
    @classmethod
    def student_id_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Student ID must not be blank")
        return value


class ScoreUpdate(BaseModel):
    score: float = Field(ge=0, allow_inf_nan=False)


class ScoreCreated(BaseModel):
    id: int
    message: str


class ResultResponse(BaseModel):
    assessment_id: int
    assessment_name: str
    subject_name: str
    score: float
    max_score: float
    percentage: float


class AverageResponse(BaseModel):
    student_id: str
    average_percentage: float
    assessment_count: int
