from fastapi import Depends
from ..repositories.user_repository import UserRepository
from ..entities.user import User
from ..viewmodels.user_model import CreateUserModel
from passlib.context import CryptContext


class AddUserUseCase:
    def __init__(self, user_repository: UserRepository = Depends()):
        self._user_repo = user_repository
        self._pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    def add(self, data: CreateUserModel):
        # TODO: check if username or email already exist
        user = User(**data.dict(exclude={'password'}), password=self._get_password_hash(data.password))
        self._user_repo.insert(user)

    def _get_password_hash(self, plain_pwd):
        return self._pwd_context.hash(plain_pwd)
