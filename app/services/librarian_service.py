from typing import Optional, List

from app.models import Librarian
from app.repositories.librarian_repository import LibrarianRepository
from app.schemas.librarian_schema import LibrarianCreate, LibrarianUpdate


class LibrarianService:
    def __init__(self, repository: LibrarianRepository):
        self.repository = repository

    def create(self, data: LibrarianCreate) -> Librarian:
        if len(data.password) < 8:
            raise ValueError("Password must be at least 8 characters")
        return self.repository.create(data)

    def update(self, id: int, data: LibrarianUpdate) -> Librarian:
        return self.repository.update(id, data)

    def delete(self, id: int) -> bool:
        return self.repository.delete(id)

    def get_by_id(self, id: int) -> Optional[Librarian]:
        return self.repository.get_by_id(id)

    def get_by_email(self, email: str) -> Optional[Librarian]:
        return self.repository.get_by_email(email)

    def get_all(self) -> List[Librarian]:
        return self.repository.get_all()