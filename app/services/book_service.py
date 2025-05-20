from typing import Optional, List

from app.models import Book
from app.repositories.book_repository import BookRepository
from app.schemas.book_schema import BookCreate, BookUpdate


class BookService:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    def create(self, data: BookCreate) -> Book:
        try:
            if self.repository.exists_by_isbn(data.isbn):
                raise ValueError("Book with this ISBN already exists")

            if not self.repository.author_exists(data.author):
                raise ValueError("Author does not exist in our database")

            return self.repository.create(data)
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Failed to create librarian: {str(e)}") from e

    def update(self, id: int, data: BookUpdate) -> Book:
        try:
            if not self.repository.exists(id):
                raise ValueError("Book not found")

            if data.isbn and self.repository.isbn_exists_except_current(data.isbn, id):
                raise ValueError("Another book with this ISBN already exists")

            return self.repository.update(id, data)
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Failed to update librarian: {str(e)}") from e

    def delete(self, id: int) -> bool:
        try:
            book = self.repository.get_by_id(id)
            if not book:
                raise ValueError("Book not found")

            if book.has_active_borrowings():
                raise ValueError("Cannot delete book with active borrowings")

            return self.repository.delete(id)
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Failed to delete librarian: {str(e)}") from e

    def get_by_id(self, id: int) -> Optional[Book]:
        try:
            book = self.repository.get_by_id(id)
            if not book:
                raise ValueError("Book not found")
            return book
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Failed to get librarian: {str(e)}") from e

    def get_all(self) -> List[Book]:
        try:
            return self.repository.get_all()
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Failed to get librarian: {str(e)}") from e
