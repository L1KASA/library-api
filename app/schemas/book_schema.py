from datetime import datetime
from typing import Optional

from pydantic import Field

from app.schemas.base_schema import BaseSchema


class BookBase(BaseSchema):
    name: str = Field(..., max_length=255)
    author: str = Field(..., max_length=255)
    year: int = Field(..., gt=0)
    isbn: str = Field(..., max_length=17)
    number_of_copies: int = Field(1, ge=0)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseSchema):
    name: Optional[str] = Field(None, max_length=255)
    author: Optional[str] = Field(None, max_length=255)
    year: Optional[int] = Field(None, gt=0)
    isbn: Optional[str] = Field(None)
    number_of_copies: Optional[int] = Field(None, ge=0)


class BookResponse(BookBase):
    id: int
    author: str
    created_at: datetime
    updated_at: datetime
