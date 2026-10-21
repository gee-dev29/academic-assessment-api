from pydantic import BaseModel, ConfigDict, Field, field_validator


class SubjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name must not be blank")
        return value


class SubjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class AssessmentCreate(BaseModel):
    subject_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=100)
    max_score: float = Field(gt=0, allow_inf_nan=False)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name must not be blank")
        return value


class AssessmentResponse(BaseModel):
    id: int
    subject_id: int
    name: str
    max_score: float


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
