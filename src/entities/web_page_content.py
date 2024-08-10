import hashlib

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, String, Integer

from ..repositories.database import Base
from ..repositories.vector_embeddings import get_embedding_model


class WebContent(Base):
    __tablename__ = "web_content"

    id = Column(Integer, primary_key=True, index=True)
    encoded_url: str = Column(String, nullable=False, index=True, unique=False)
    url = Column(String, nullable=False)
    page_content = Column(String, nullable=False)
    embeddings = Column(Vector(len(get_embedding_model().embed_query("test"))), nullable=False)


def encode_url(url):
    return hashlib.md5(url.encode()).hexdigest()
