from typing import List, Optional
from sqlalchemy import and_, select, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from app.models.borrowed_book_model import BorrowedBook


class BorrowedBookRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, book_id: int, reader_id: int, librarian_id: int) -> BorrowedBook:
        try:
            borrowed_book = BorrowedBook(
                book_id=book_id,
                reader_id=reader_id,
                librarian_id=librarian_id
            )
            self.db.add(borrowed_book)
            self.db.commit()
            self.db.refresh(borrowed_book)
            return borrowed_book
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Database integrity error when crating borrowed book: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error when creating borrowed book: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Borrowed book create error: {str(e)}")

    def get_active_borrowings(self, reader_id: int) -> List[BorrowedBook]:
        try:
            stmt = select(BorrowedBook).where(
                and_(
                    BorrowedBook.reader_id == reader_id,
                    BorrowedBook.returned_date.is_(None)
                )
            )
            return list(self.db.execute(stmt).scalars().all())
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error when getting active borrowed books: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Borrowed book get active borrowings error: {str(e)}")

    def get_active_borrowing(self, book_id: int, reader_id: int) -> Optional[BorrowedBook]:
        try:
            stmt = select(BorrowedBook).where(
                and_(
                    BorrowedBook.book_id == book_id,
                    BorrowedBook.reader_id == reader_id,
                    BorrowedBook.returned_date.is_(None)
                )
            )
            return self.db.execute(stmt).scalar_one_or_none()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error when getting active borrowed book: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Borrowed book get active borrowing error: {str(e)}")

    def get_all_borrowings(self) -> List[BorrowedBook]:
        try:
            stmt = select(BorrowedBook)
            return self.db.execute(stmt).scalars().all()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error when getting active borrowed books: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Borrowed book get active borrowing error: {str(e)}")

    def mark_returned(self, borrowing_id: int) -> BorrowedBook:
        try:
            borrowing = self.db.get(BorrowedBook, borrowing_id)
            if borrowing:
                borrowing.returned_date = func.now()
                self.db.commit()
                self.db.refresh(borrowing)
            return borrowing
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error when marking borrowed book: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Borrowed book mark error: {str(e)}")

    def has_active_borrows_for_book(self, book_id: int) -> bool:
        try:
            statement = select(BorrowedBook).where(
                BorrowedBook.book_id == book_id,
                BorrowedBook.returned_date.is_(None)
            ).limit(1)
            return self.db.execute(statement).scalar_one_or_none() is not None
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error when checking active loans: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Active loans check error: {str(e)}")
