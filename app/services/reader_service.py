from typing import Optional, List

from app.models import Reader
from app.repositories.reader_repository import ReaderRepository
from app.schemas.reader_schema import ReaderCreate, ReaderUpdate


class ReaderService:
    def __init__(self, repository: ReaderRepository):
        self.repository = repository

    def create(self, data: ReaderCreate) -> Reader:
        return self.repository.create(data)

    def update(self, id: int, data: ReaderUpdate) -> Reader:
        return self.repository.update(id, data)

    def delete(self, id: int) -> bool:
        return self.repository.delete(id)

    def get_by_id(self, id: int) -> Optional[Reader]:
        return self.repository.get_by_id(id)

    def get_by_email(self, email: str) -> Optional[Reader]:
        return self.repository.get_by_email(email)

    def get_all(self) -> List[Reader]:
        return self.repository.get_all()