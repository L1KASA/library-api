from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base_model import Base


class Person(Base):
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    surname: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)

    librarian: Mapped["Librarian"] = relationship(back_populates="person", cascade="all, delete")
    reader: Mapped["Reader"] = relationship(back_populates="person", cascade="all, delete")
