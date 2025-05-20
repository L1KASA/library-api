from typing import List

from app.models.borrowed_book_model import BorrowedBook
from app.repositories.book_repository import BookRepository
from app.repositories.borrowed_book_repository import BorrowedBookRepository
from app.repositories.reader_repository import ReaderRepository


class BorrowedBookService:
    def __init__(
            self,
            book_repo: BookRepository,
            borrow_repo: BorrowedBookRepository,
            reader_repo: ReaderRepository,
    ):
        self.book_repo = book_repo
        self.borrow_repo = borrow_repo
        self.reader_repo = reader_repo

    def borrow_book(self, book_id: int, reader_id: int, librarian_id: int) -> BorrowedBook:
        try:
            if not self.reader_repo.reader_exists(reader_id):
                raise ValueError(f"Reader with ID {reader_id} not found")

            if not self.book_repo.is_book_available(book_id):
                raise ValueError("Book is not available for borrowing")

            if len(self.borrow_repo.get_active_borrowings(reader_id)) >= 3:
                raise ValueError("Reader has reached the maximum number of borrowed books")

            self.book_repo.decrease_book_copies(book_id)

            return self.borrow_repo.create(book_id, reader_id, librarian_id)
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Failed to borrow book {str(e)}") from e

    def return_book(self, book_id: int, reader_id: int) -> BorrowedBook:
        try:
            borrowing = self.borrow_repo.get_active_borrowing(book_id, reader_id)
            if not borrowing:
                raise ValueError("No active borrowing record found")

            self.book_repo.increase_book_copies(book_id)

            return self.borrow_repo.mark_returned(borrowing.id)
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Failed to borrow book {str(e)}") from e

    def get_active_borrowings(self, reader_id: int) -> List[BorrowedBook]:
        try:
            if not self.reader_repo.reader_exists(reader_id):
                raise ValueError(f"Reader with ID {reader_id} not found")
            return self.borrow_repo.get_active_borrowings(reader_id)
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Failed to borrow book: {str(e)}") from e

    def get_all_active_borrowings(self) -> List[BorrowedBook]:
        try:
            return self.borrow_repo.get_all_borrowings()
        except Exception as e:
            raise ValueError(f"Failed to get all active borrowings: {str(e)}") from e
