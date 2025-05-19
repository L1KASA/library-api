from datetime import datetime
from typing import Optional

from pydantic import Field

from app.schemas.base_schema import BaseSchema
from app.schemas.person_schema import PersonCreate, PersonUpdate, PersonResponse


class LibrarianCreate(BaseSchema):
    person: PersonCreate
    password: str = Field(..., min_length=8)

class LibrarianUpdate(BaseSchema):
    person: Optional[PersonUpdate] = None

class LibrarianResponse(BaseSchema):
    id: int
    person: PersonResponse
    created_at: datetime
    updated_at: datetime
