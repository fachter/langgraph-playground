from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Type

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from . import URL

engine = create_engine(URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):

    def __init__(self, db: Session = Depends(get_db)):
        self._db = db

    @abstractmethod
    def get_type(self) -> Type[T]:
        raise NotImplementedError()

    def find_by_id(self, entity_id: int) -> Optional[T]:
        return self._db.query(self.get_type()).get(entity_id)

    def insert(self, entity: T) -> T:
        self._db.add(entity)
        self._db.commit()
        self._db.refresh(entity)
        return entity

    def insert_many(self, entities: List[T]) -> List[T]:
        self._db.add_all(entities)
        self._db.commit()
        self._db.refresh(entities)
        return entities

    def find_all(self) -> List[T]:
        return self._db.query(T).all()
