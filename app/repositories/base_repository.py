from abc import ABC, abstractmethod
from typing import List, Generic, TypeVar
from pydantic import BaseModel
from app.models import Base

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class AbstractBaseRepository(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    @abstractmethod
    def create(self, data: CreateSchemaType) -> ModelType:
        raise NotImplementedError

    @abstractmethod
    def update(self, id: int, data: UpdateSchemaType) -> ModelType:
        raise NotImplementedError

    @abstractmethod
    def delete(self, id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> List[ModelType]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, id: int) -> ModelType:
        raise NotImplementedError
