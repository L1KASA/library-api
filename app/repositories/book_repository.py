from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Book
from app.repositories.base_repository import AbstractBaseRepository
from app.schemas.book_schema import BookCreate, BookUpdate


class BookRepository(AbstractBaseRepository[Book, BookCreate, BookUpdate]):
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: BookCreate) -> Book:
        try:
            book = Book(**data.model_dump())
            self.db.add(book)
            self.db.commit()
            self.db.refresh(book)
            return book
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Book creation error: {str(e)}")

    def update(self, id: int, data: BookUpdate) -> Book:
        book = self.db.get(Book, id)
        if book is None:
            raise ValueError(f"Book with id {id} not found")

        if data.number_of_copies < 0:
            raise ValueError(f"Number of copies {data.number_of_copies} must be positive")

        book_data = data.model_dump(exclude_unset=True)
        for key, value in book_data.items():
            setattr(book, key, value)

        self.db.commit()
        self.db.refresh(book)
        return book

    def delete(self, id: int) -> bool:
        book = self.db.get(Book, id)
        if book is None:
            return False

        try:
            self.db.delete(book)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    def get_by_id(self, id: int) -> Optional[Book]:
        statement = select(Book).where(Book.id == id)
        return self.db.execute(statement).scalar_one_or_none()

    def get_all(self) -> List[Book]:
        statement = select(Book)
        return list(self.db.execute(statement).scalars().unique())