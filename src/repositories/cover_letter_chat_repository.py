from typing import Type

from src.repositories.database import BaseRepository, T


class CoverLetterChatRepository(BaseRepository[CoverLetterChat]):
    def get_type(self) -> Type[T]:
        return CoverLetterChat

