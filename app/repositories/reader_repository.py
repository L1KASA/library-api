from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Reader
from app.models.person_model import Person
from app.repositories.base_repository import AbstractBaseRepository
from app.schemas.reader_schema import ReaderUpdate, ReaderCreate


class ReaderRepository(AbstractBaseRepository[Reader, ReaderCreate, ReaderUpdate]):
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: ReaderCreate) -> Reader:
        try:
            person = Person(**data.person.model_dump())

            reader = Reader(
                person=person,
            )

            self.db.add(reader)
            self.db.commit()
            self.db.refresh(reader)
            return reader
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Reader creation error: {str(e)}")

    def update(self, id: int, data: ReaderUpdate) -> Reader:
        reader = self.db.get(Reader, id)
        if reader is None:
            raise ValueError(f"Reader with id {id} not found")

        if data.person:
            person_data = data.person.model_dump(exclude_unset=True)
            for key, value in person_data.items():
                setattr(reader, key, value)

        self.db.commit()
        self.db.refresh(reader)
        return reader

    def delete(self, id: int) -> bool:
        reader = self.db.get(Reader, id)
        if reader is None:
            return False

        try:
            self.db.delete(reader.person)
            self.db.delete(reader)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    def get_by_id(self, id: int) -> Optional[Reader]:
        statement = select(Reader).join(Person).where(Reader.id == id)
        return self.db.execute(statement).scalar_one_or_none()

    def get_by_email(self, email: str) -> Optional[Reader]:
        statement = select(Reader).join(Person).where(Person.email == email)
        return self.db.execute(statement).scalar_one_or_none()

    def get_all(self) -> List[Reader]:
        statement = select(Reader).join(Person)
        return self.db.execute(statement).scalars().all()