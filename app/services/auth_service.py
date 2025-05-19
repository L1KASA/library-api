import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.schemas.librarian_schema import LibrarianUpdate
from app.utills import security
from app.utills.security import verify_password, get_password_hash

from app.models import Librarian
from app.repositories.librarian_repository import LibrarianRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, repository: LibrarianRepository):
        self.repository = repository
        self.SECRET_KEY = os.environ.get("SECRET_KEY")
        self.ALGORITHM = os.environ.get("ALGORITHM")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))

    def authenticate(self, email: str, password: str) -> Optional[Librarian]:
        librarian = self.repository.get_by_email(email)
        if not librarian:
            return None
        if not verify_password(password, librarian.hash_password):
            return None
        return librarian

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except JWTError:
            return {}

    def change_password(
            self, current_password: str,
            new_password: str,
            librarian: Librarian) -> Librarian:
        if not verify_password(current_password, librarian.hash_password):
            raise ValueError("Current password is incorrect")

        librarian.hash_password = get_password_hash(new_password)

        updated_librarian = self.repository.change_password(
            id=librarian.id,
            data=LibrarianUpdate(password=new_password)
        )

        return updated_librarian
