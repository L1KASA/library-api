from datetime import datetime
from typing import Optional

from app.schemas.base_schema import BaseSchema


class BorrowedBookBase(BaseSchema):
    book_id: int
    reader_id: int
    librarian_id: int


class BorrowedBookCreate(BorrowedBookBase):
    pass


class BorrowedBookResponse(BorrowedBookBase):
    id: int
    borrowed_date: datetime
    returned_date: Optional[datetime]
