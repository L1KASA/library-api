from app.repositories.base_repository import AbstractBaseRepository


class BaseService:
    def __init__(self, repository: AbstractBaseRepository):
        pass
        #self.repository: SqlAlchemy

    def create(self):
        pass

    def update(self, id: int):
        pass

    def delete(self, id: int):
        pass

    def get_all(self):
        pass

    def get_by_id(self, id: int):
        pass