from typing import Optional, Type

from .database import BaseRepository
from ..entities.user import User


class UserRepository(BaseRepository[User]):

    def get_type(self) -> Type[User]:
        return User

    def find_one_by_username(self, username) -> Optional[User]:
        return self._db.query(User).filter(User.username == username).one_or_none()
