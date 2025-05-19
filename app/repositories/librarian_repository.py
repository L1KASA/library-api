from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.librarian_model import Librarian
from app.models.person_model import Person
from app.repositories.base_repository import AbstractBaseRepository, ModelType, CreateSchemaType, UpdateSchemaType
from app.schemas.librarian_schema import LibrarianCreate, LibrarianUpdate
from app.utills.security import get_password_hash


class LibrarianRepository(AbstractBaseRepository[Librarian, LibrarianCreate, LibrarianUpdate]):
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: LibrarianCreate) -> Librarian:
        try:
            person = Person(**data.person.model_dump())

            hashed_password = get_password_hash(data.password)

            librarian = Librarian(
                person=person,
                hash_password=hashed_password,
            )

            self.db.add(librarian)
            self.db.commit()
            self.db.refresh(librarian)
            return librarian
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Librarian creation error: {str(e)}")

    def update(self, id: int, data: LibrarianUpdate) -> Librarian:
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

    def delete(self, id: int) -> bool:
        librarian = self.db.get(Librarian, id)
        if librarian is None:
            return False

        try:
            self.db.delete(librarian.person)
            self.db.delete(librarian)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    def change_password(self, id: int, data: LibrarianUpdate) -> Librarian:
        librarian = self.db.get(Librarian, id)
        if librarian is None:
            raise ValueError(f"Librarian with id {id} not found")

        if data.password:
            librarian.hash_password = get_password_hash(data.password)
        self.db.commit()
        self.db.refresh(librarian)
        return librarian

    def get_by_id(self, id: int) -> Optional[Librarian]:
        statement = select(Librarian).join(Person).where(Librarian.id == id)
        return self.db.execute(statement).scalar_one_or_none()

    def get_by_email(self, email: str) -> Optional[Librarian]:
        statement = select(Librarian).join(Person).where(Person.email == email)
        return self.db.execute(statement).scalar_one_or_none()

    def get_all(self) -> List[Librarian]:
        statement = select(Librarian).join(Person)
        return self.db.execute(statement).scalars().all()
