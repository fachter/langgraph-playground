from sqlalchemy import Column, Integer

from ..repositories.database import Base


class CoverLetterChat(Base):
    __tablename__ = 'cover_letter_chat'
    id = Column(Integer, primary_key=True, index=True)

