from typing import List, Type

from fastapi import Depends
from sqlalchemy.orm import Session

from src.entities.web_page_content import WebContent
from src.repositories.database import get_db


class WebContentRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self._db = db

    def find_all_by_encoded_url(self, encoded_url) -> List[Type[WebContent]]:
        return (
            self._db.query(WebContent)
            .filter(WebContent.encoded_url == encoded_url)
            .all()
        )

    def insert(self, web_content: WebContent) -> WebContent:
        self._db.add(web_content)
        self._db.commit()
        self._db.refresh(web_content)
        return web_content

    def insert_many(self, web_contents: List[WebContent]) -> List[WebContent]:
        self._db.add_all(web_contents)
        self._db.commit()
        self._db.refresh(web_contents)
        return web_contents
