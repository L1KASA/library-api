from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.librarian_model import Librarian
from app.models.person_model import Person
from app.repositories.base_repository import AbstractBaseRepository
from app.schemas.librarian_schema import LibrarianRepoCreate, LibrarianRepoUpdate
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


class LibrarianRepository(AbstractBaseRepository[Librarian, LibrarianRepoCreate, LibrarianRepoUpdate]):
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: LibrarianRepoCreate) -> Librarian:
        try:
            person = Person(**data.person.model_dump())

            librarian = Librarian(
                person=person,
                hash_password=data.hashed_password,
            )

            self.db.add(librarian)
            self.db.commit()
            self.db.refresh(librarian)
            return librarian
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Database integrity error when creating librarian: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error when creating librarian: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Librarian creation error: {str(e)}")

    def update(self, id: int, data: LibrarianRepoUpdate) -> Librarian:
        try:
            librarian = self.db.get(Librarian, id)
            if librarian is None:
                raise ValueError(f"Librarian with id {id} not found")

            if data.person:
                person_data = data.person.model_dump(exclude_unset=True)
                for key, value in person_data.items():
                    setattr(librarian.person, key, value)

            self.db.commit()
            self.db.refresh(librarian)
            return librarian
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error when updating librarian: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Librarian update error: {str(e)}")

    def delete(self, id: int) -> bool:
        try:
            librarian = self.db.get(Librarian, id)
            if librarian is None:
                return False

            self.db.delete(librarian.person)
            self.db.delete(librarian)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Librarian delete error: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Database error when deleting librarian: {str(e)}")

    def change_password(self, id: int, hashed_password: str) -> Librarian:
        try:
            librarian = self.db.get(Librarian, id)
            if librarian is None:
                raise ValueError(f"Librarian with id {id} not found")

            librarian.hash_password = hashed_password
            self.db.commit()
            self.db.refresh(librarian)
            return librarian
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error when changing password for librarian: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Librarian change password error: {str(e)}")

    def get_by_id(self, id: int) -> Optional[Librarian]:
        try:
            statement = select(Librarian).join(Person).where(Librarian.id == id)
            return self.db.execute(statement).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Database error when getting librarian: {str(e)}") from e
        except Exception as e:
            raise Exception(f"Unexpected error getting librarian: {str(e)}") from e

    def get_by_email(self, email: str) -> Optional[Librarian]:
        try:
            statement = select(Librarian).join(Person).where(Person.email == email)
            librarian = self.db.execute(statement).scalar_one_or_none()
            if librarian:
                return librarian

        except SQLAlchemyError as e:
            raise ValueError(f"Database error when getting librarian: {str(e)}")
        except Exception as e:
            raise ValueError(f"Librarian get by email error: {str(e)}")

    def get_all(self) -> List[Librarian]:
        try:
            statement = select(Librarian).join(Person)
            return self.db.execute(statement).scalars().all()
        except SQLAlchemyError as e:
            raise ValueError(f"Database error when getting librarian: {str(e)}")
        except Exception as e:
            raise ValueError(f"Librarian get all error: {str(e)}")
