from pydantic import BaseModel, Field

class StudentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=100)

class StudentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: str | None = Field(default=None, min_length=5, max_length=100)