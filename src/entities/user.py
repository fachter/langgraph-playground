from sqlalchemy import Column, Integer, String

from ..repositories.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username: str = Column(String, unique=True)
    first_name: str = Column(String)
    last_name: str = Column(String)
    email: str = Column(String)
    password: str = Column(String)
