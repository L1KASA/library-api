from passlib.context import CryptContext
from pydantic import SecretStr
from pydantic_settings import BaseSettings


class SecuritySettings(BaseSettings):
    secret_key: SecretStr
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


class PasswordSecurity:
    def __init__(self):
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self._min_password_length = 8

    def get_password_hash(self, password: SecretStr) -> str:
        return self._pwd_context.hash(password.get_secret_value())

    def verify_password(self, password: SecretStr, hashed_password: str) -> bool:
        self._validate_password(password)
        return self._pwd_context.verify(password.get_secret_value(), hashed_password)

    def _validate_password(self, password: SecretStr) -> None:
        if len(password.get_secret_value()) < self._min_password_length:
            raise ValueError("Password is too short.")
