from typing import Optional

from pydantic import Field, EmailStr

from app.schemas.base_schema import BaseSchema


class PersonBase(BaseSchema):
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    surname: Optional[str] = Field(..., max_length=50)
    email: EmailStr = Field(..., max_length=254)


class PersonCreate(PersonBase):
    pass


class PersonUpdate(BaseSchema):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    surname: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=254)


class PersonResponse(PersonBase):
    pass
