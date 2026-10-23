from pydantic import BaseModel, Field, field_validator


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
