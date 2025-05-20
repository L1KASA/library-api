from typing import Optional

from pydantic import BaseModel, EmailStr, Field, SecretStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[EmailStr] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: SecretStr


class ChangePasswordRequest(BaseModel):
    current_password: SecretStr
    new_password: SecretStr = Field(..., min_length=8)
