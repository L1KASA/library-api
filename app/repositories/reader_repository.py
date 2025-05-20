from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
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
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Database integrity error when creating reader: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error when creating reader: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Unexpected error when creating reader: {str(e)}")

    def update(self, id: int, data: ReaderUpdate) -> Reader:
        try:
            reader = self.db.get(Reader, id)
            if reader is None:
                raise ValueError(f"Reader with id {id} not found")

            if data.person:
                person_data = data.person.model_dump(exclude_unset=True)
                for key, value in person_data.items():
                    setattr(reader.person, key, value)

            self.db.commit()
            self.db.refresh(reader)
            return reader
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error when updating reader: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Unexpected error when updating reader: {str(e)}")

    def delete(self, id: int) -> bool:
        try:
            reader = self.db.get(Reader, id)
            if reader is None:
                raise ValueError(f"Reader with id {id} not found")

            unreturned_books = [
                borrowing for borrowing in reader.borrowings
                if borrowing.returned_date is None
            ]

            if unreturned_books:
                raise ValueError("Cannot delete reader with unreturned books")

            self.db.delete(reader.person)
            self.db.delete(reader)
            self.db.commit()
            return True
        except ValueError as e:
            self.db.rollback()
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Database error when deleting reader: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Unexpected error when deleting reader: {str(e)}")

    def get_by_id(self, id: int) -> Optional[Reader]:
        try:
            statement = select(Reader).join(Person).where(Reader.id == id)
            return self.db.execute(statement).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise ValueError(f"Database error when getting reader by id: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error when getting reader by id: {str(e)}")

    def get_by_email(self, email: str) -> Optional[Reader]:
        try:
            statement = select(Reader).join(Person).where(Person.email == email)
            return self.db.execute(statement).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise ValueError(f"Database error when getting reader by email: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error when getting reader by email: {str(e)}")

    def get_all(self) -> List[Reader]:
        try:
            statement = select(Reader).join(Person)
            return self.db.execute(statement).scalars().all()
        except SQLAlchemyError as e:
            raise ValueError(f"Database error when getting all readers: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error when getting all readers: {str(e)}")

    def reader_exists(self, reader_id: int) -> bool:
        try:
            return self.db.get(Reader, reader_id) is not None
        except SQLAlchemyError as e:
            raise ValueError(f"Database error when checking reader existence: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error when checking reader existence: {str(e)}")
