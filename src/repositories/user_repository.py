from typing import Optional

from fastapi import Depends
from sqlalchemy.orm import Session

from .database import get_db
from ..entities.user import User


class UserRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self._db = db

    def find_one_by_username(self, username) -> Optional[User]:
        return self._db.query(User).filter(User.username == username).one_or_none()

    def insert(self, user: User) -> User:
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user

