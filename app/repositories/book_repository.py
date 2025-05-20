from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Book
from app.models.borrowed_book_model import BorrowedBook
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
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Database integrity error when creating book: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error when creating book: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Book creation error: {str(e)}")

    def update(self, id: int, data: BookUpdate) -> Book:
        try:
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
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error when updating book: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Book update error: {str(e)}")

    def delete(self, id: int) -> bool:
        try:
            book = self.db.get(Book, id)
            if book is None:
                return False

            self.db.delete(book)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error when deleting book: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Book deletion error: {str(e)}")

    def get_by_id(self, id: int) -> Optional[Book]:
        try:
            statement = select(Book).where(Book.id == id)
            return self.db.execute(statement).scalar_one_or_none()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error when retrieving book: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Book retrieval error: {str(e)}")

    def get_all(self) -> List[Book]:
        try:
            statement = select(Book)
            return list(self.db.execute(statement).scalars().unique())
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error when retrieving books: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Book retrieval error: {str(e)}")

    def is_book_available(self, book_id: int) -> bool:
        try:
            book = self.db.get(Book, book_id)
            return book and book.number_of_copies > 0
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error when checking book: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Book retrieval error: {str(e)}")

    def decrease_book_copies(self, book_id: int):
        try:
            book = self.db.get(Book, book_id)
            if book is None:
                raise ValueError(f"Book with id {book_id} not found")
            if book.number_of_copies <= 0:
                raise ValueError("Cannot decrease copies - no copies available")

            book.number_of_copies -= 1
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error when decreasing book copies: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Unexpected error when decreasing book copies: {str(e)}")

    def increase_book_copies(self, book_id: int):
        try:
            book = self.db.get(Book, book_id)
            if book is None:
                raise ValueError(f"Book with id {book_id} not found")

            book.number_of_copies += 1
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error when increasing book copies: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Unexpected error when increasing book copies: {str(e)}")

    def exists(self, id: int) -> bool:
        try:
            statement = select(Book).where(Book.id == id)
            return self.db.execute(statement).scalar_one_or_none() is not None
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error when checking book existence: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Book existence check error: {str(e)}")

    def exists_by_isbn(self, isbn: str) -> bool:
        try:
            statement = select(Book).where(Book.isbn == isbn)
            return self.db.execute(statement).scalar_one_or_none() is not None
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error when checking ISBN existence: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"ISBN existence check error: {str(e)}")

    def isbn_exists_except_current(self, isbn: str, current_id: int) -> bool:
        try:
            statement = select(Book).where(Book.isbn == isbn, Book.id != current_id)
            return self.db.execute(statement).scalar_one_or_none() is not None
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error when checking ISBN existence: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"ISBN existence check error: {str(e)}")

    def author_exists(self, author: str) -> bool:
        try:
            statement = select(Book).where(Book.author == author).limit(1)
            return self.db.execute(statement).scalar_one_or_none() is not None
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error when checking author existence: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Author existence check error: {str(e)}")
