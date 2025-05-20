from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base_model import Base


class Reader(Base):
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"))

    person: Mapped["Person"] = relationship(back_populates="reader", cascade="all, delete")

    borrowings: Mapped[list["BorrowedBook"]] = relationship("BorrowedBook", back_populates="reader",
                                                            cascade="all, delete")
