from typing import Optional, List

from sqlalchemy.exc import SQLAlchemyError

from app.models import Librarian
from app.repositories.librarian_repository import LibrarianRepository
from app.schemas.librarian_schema import LibrarianCreate, LibrarianUpdate, LibrarianRepoCreate, LibrarianRepoUpdate
from app.utils.security import PasswordSecurity

class LibrarianService:
    def __init__(self, repository: LibrarianRepository, password_security: PasswordSecurity):
        self.repository = repository
        self.password_security = password_security

    def create(self, data: LibrarianCreate) -> Librarian:
        try:
            if self.repository.get_by_email(data.person.email):
                raise ValueError("Email already in use")

            hashed_password = self.password_security.get_password_hash(data.password)
            repo_data = LibrarianRepoCreate(
                person=data.person,
                hashed_password=hashed_password
            )
            return self.repository.create(repo_data)
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Failed to create librarian: {str(e)}") from e


    def update(self, id: int, data: LibrarianUpdate) -> Librarian:
        try:
            existing_librarian = self.repository.get_by_id(id)
            if not existing_librarian:
                raise ValueError("Librarian not found")

            if data.person and data.person.email and data.person.email != existing_librarian.person.email:
                if self.repository.get_by_email(data.person.email):
                    raise ValueError("New email already in use")

            repo_update_data = LibrarianRepoUpdate(person=data.person)
            return self.repository.update(id, repo_update_data)
        except Exception as e:
            raise ValueError(f"Failed to update librarian: {str(e)}") from e

    def delete(self, id: int) -> bool:
        try:
            librarian = self.repository.get_by_id(id)
            if not librarian:
                raise ValueError("Librarian not found")

            return self.repository.delete(id)
        except Exception as e:
            raise ValueError(f"Failed to delete librarian: {str(e)}") from e

    def get_by_id(self, id: int) -> Optional[Librarian]:
        try:
            librarian = self.repository.get_by_id(id)
            if not librarian:
                raise ValueError("Librarian not found")
            return librarian
        except SQLAlchemyError as e:
            raise ValueError("Failed to get librarian") from e
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError("Librarian get by id error") from e

    def get_by_email(self, email: str) -> Optional[Librarian]:
        try:
            if "@" not in email:
                raise ValueError("Invalid email format")

            librarian = self.repository.get_by_email(email)
            if not librarian:
                raise ValueError("Librarian not found")
            return librarian
        except SQLAlchemyError as e:
            raise ValueError("Failed to get librarian by email") from e
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError("Librarian get by email error") from e

    def get_all(self) -> List[Librarian]:
        try:
            librarians = self.repository.get_all()
            if not librarians:
                raise ValueError("No librarians found")
            return librarians
        except SQLAlchemyError as e:
            raise ValueError("Failed to get all librarians") from e
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError("Librarian get all error") from e
