from typing import Optional, List

from app.models import Book
from app.repositories.book_repository import BookRepository
from app.schemas.book_schema import BookCreate, BookUpdate


class BookService:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    def create(self, data: BookCreate) -> Book:
        return self.repository.create(data)

    def update(self, id: int, data: BookUpdate) -> Book:
        return self.repository.update(id, data)

    def delete(self, id: int) -> bool:
        return self.repository.delete(id)

    def get_by_id(self, id: int) -> Optional[Book]:
        return self.repository.get_by_id(id)

    def get_all(self) -> List[Book]:
        return self.repository.get_all()