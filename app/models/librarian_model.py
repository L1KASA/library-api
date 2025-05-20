from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base_model import Base


class Librarian(Base):
    hash_password: Mapped[str] = mapped_column(String(60), nullable=False)
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"))

    person: Mapped["Person"] = relationship(back_populates="librarian", cascade="all, delete")

    borrowings: Mapped[list["BorrowedBook"]] = relationship("BorrowedBook", back_populates="librarian")
