from typing import List, Type

from src.entities.web_page_content import WebContent
from src.repositories.database import BaseRepository, T


class WebContentRepository(BaseRepository[WebContent]):

    def get_type(self) -> Type[T]:
        return WebContent

    def find_all_by_encoded_url(self, encoded_url) -> List[Type[WebContent]]:
        return (
            self._db.query(WebContent)
            .filter(WebContent.encoded_url == encoded_url)
            .all()
        )
