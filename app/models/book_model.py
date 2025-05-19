from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.models.base_model import Base
from app.models.borrowed_book_model import BorrowedBook


class Book(Base):
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    year: Mapped[int] = mapped_column()
    isbn: Mapped[str] = mapped_column(String(17), unique=True, nullable=True)
    number_of_copies: Mapped[int] = mapped_column(default=1)

    borrowings: Mapped[list["BorrowedBook"]] = relationship("BorrowedBook", back_populates="book")

    @validates('number_of_copies')
    def validate_number_of_copies(self, key, value):
        if value < 0:
            raise ValueError("Number of copies cannot be negative")
        return value
