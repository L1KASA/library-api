from typing import Optional, List

from sqlalchemy.exc import SQLAlchemyError

from app.models import Reader
from app.repositories.reader_repository import ReaderRepository
from app.schemas.reader_schema import ReaderCreate, ReaderUpdate


class ReaderService:
    def __init__(self, repository: ReaderRepository):
        self.repository = repository

    def create(self, data: ReaderCreate) -> Reader:
        try:
            if self.repository.get_by_email(data.person.email):
                raise ValueError("Email already in use")

            return self.repository.create(data)
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Failed to create reader: {str(e)}") from e

    def update(self, id: int, data: ReaderUpdate) -> Reader:
        try:
            existing_reader = self.repository.get_by_id(id)
            if not existing_reader:
                raise ValueError("Reader not found")

            if data.person and data.person.email and data.person.email != existing_reader.person.email:
                if self.repository.get_by_email(data.person.email):
                    raise ValueError("New email already in use")

            return self.repository.update(id, data)
        except Exception as e:
            raise ValueError(f"Failed to update reader: {str(e)}") from e

    def delete(self, id: int) -> bool:
        try:
            reader = self.repository.get_by_id(id)
            if not reader:
                raise ValueError("Reader not found")

            return self.repository.delete(id)
        except ValueError as e:
            if "Cannot delete reader with borrowed books" in str(e):
                raise ValueError(
                    "Reader cannot be deleted because they have unreturned books. "
                    "Please return all books first.")
            raise
        except Exception as e:
            raise ValueError(f"Failed to delete reader: {str(e)}") from e

    def get_by_id(self, id: int) -> Optional[Reader]:
        try:
            reader = self.repository.get_by_id(id)
            if not reader:
                raise ValueError("Reader not found")
            return reader
        except SQLAlchemyError as e:
            raise ValueError("Failed to get reader") from e
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Failed to get reader: {str(e)}") from e

    def get_by_email(self, email: str) -> Optional[Reader]:
        try:
            if "@" not in email:
                raise ValueError("Invalid email format")
            reader = self.repository.get_by_email(email)
            if not reader:
                raise ValueError("Reader not found")
            return reader
        except SQLAlchemyError as e:
            raise ValueError("Failed to get reader by email") from e
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Failed to get reader: {str(e)}") from e

    def get_all(self) -> List[Reader]:
        try:
            readers = self.repository.get_all()
            if not readers:
                raise ValueError("No readers found")
            return readers
        except SQLAlchemyError as e:
            raise ValueError("Failed to get all readers") from e
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Failed to get readers: {str(e)}") from e
