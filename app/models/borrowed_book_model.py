from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, DateTime, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class BorrowedBook(Base):
    book_id: Mapped[int] = mapped_column(ForeignKey('books.id'), nullable=False)
    reader_id: Mapped[int] = mapped_column(ForeignKey('readers.id'), nullable=False)
    librarian_id: Mapped[str] = mapped_column(ForeignKey('librarians.id'), nullable=False)

    borrowed_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )
    returned_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )

    book: Mapped['Book'] = relationship("Book", back_populates="borrowings")
    reader: Mapped['Reader'] = relationship("Reader", back_populates="borrowings")
    librarian: Mapped['Librarian'] = relationship("Librarian", back_populates="borrowings")