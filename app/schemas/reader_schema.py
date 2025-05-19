from datetime import datetime
from typing import Optional

from app.schemas.base_schema import BaseSchema
from app.schemas.person_schema import PersonCreate, PersonUpdate, PersonResponse


class ReaderCreate(BaseSchema):
    person: PersonCreate

class ReaderUpdate(BaseSchema):
    person: Optional[PersonUpdate] = None

class ReaderResponse(BaseSchema):
    id: int
    person: PersonResponse
    created_at: datetime
    updated_at: datetime
