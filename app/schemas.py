from pydantic import BaseModel, ConfigDict, EmailStr, Field

class StudentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    age: int = Field(ge=1, le=40)
    course: str = Field(min_length=2, max_length=100)

class StudentUpdate(BaseModel):
    
    name:  str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    email: EmailStr | None = None

    age: int | None = Field(
        default=None,
        ge=1,
        le=100
    )

    course: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

class StudentResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    age: int
    course: str

    model_config = ConfigDict(from_attributes=True)