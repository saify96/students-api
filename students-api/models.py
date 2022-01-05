from datetime import date, datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel
from pydantic.fields import Field


class StudentModel(BaseModel):
    id: Optional[UUID] = uuid4()
    name: str
    department: str
    state: str
    gender: str
    date_of_birth: date
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class PostStudent(BaseModel):
    name: str = Field(example='First name', max_length=20)
    gender: str = Field(example='Gender')
    state: str = Field(example='State')
    department: str = Field(example='Department')
    date_of_birth: date


class PutStudent(PostStudent):
    created_at: datetime
    updated_at: datetime


class PatchStudent(BaseModel):
    name: Optional[str] = Field(example='First name', max_length=20)
    gender: Optional[str] = Field(example='Gender')
    state: Optional[str] = Field(example='State')
    department: Optional[str] = Field(example='Department')
    date_of_birth: Optional[date]
