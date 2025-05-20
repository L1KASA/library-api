import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from pydantic import SecretStr

from app.models import Librarian
from app.repositories.librarian_repository import LibrarianRepository
from app.utils.security import SecuritySettings, PasswordSecurity


class AuthService:
    def __init__(
            self,
            repository: LibrarianRepository,
            password_security: PasswordSecurity,
            security_settings: SecuritySettings
    ):
        self.repository = repository
        self.password_security = password_security
        self.security_settings = security_settings

    def authenticate(self, email: str, password: SecretStr) -> Optional[Librarian]:
        try:
            librarian = self.repository.get_by_email(email)

            if not librarian:
                raise ValueError("Invalid email or password")

            if not self.password_security.verify_password(password, librarian.hash_password):
                raise ValueError("Invalid email or password")

            return librarian
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Authentication failed: {str(e)}") from e

    def create_access_token(self, data: dict) -> str:
        try:
            to_encode = data.copy()
            expire = (datetime.now(timezone.utc).replace(tzinfo=None)
                      + timedelta(minutes=self.security_settings.access_token_expire_minutes))

            to_encode.update({"exp": expire})
            return jwt.encode(to_encode, self.security_settings.secret_key.get_secret_value(),
                              algorithm=self.security_settings.algorithm)
        except Exception as e:
            raise ValueError(f"Failed to create access token: {str(e)}") from e

    def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                self.security_settings.secret_key.get_secret_value(),
                algorithms=[self.security_settings.algorithm]
            )

            if "sub" not in payload:
                raise ValueError("Invalid token - subject is missing")
            return payload
        except JWTError as e:
            raise ValueError("Invalid token") from e
        except Exception as e:
            raise ValueError("Token verification failed") from e

    def change_password(self, current_password: SecretStr, new_password: SecretStr, librarian: Librarian) -> Librarian:
        try:
            if not self.password_security.verify_password(current_password, librarian.hash_password):
                raise ValueError("Current password is incorrect")

            hashed_password = self.password_security.get_password_hash(new_password)

            return self.repository.change_password(librarian.id, hashed_password)
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Failed to change password: {str(e)}") from e