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
