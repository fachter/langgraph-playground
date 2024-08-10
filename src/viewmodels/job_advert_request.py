from pydantic import BaseModel, Field


class JobAdvertRequest(BaseModel):
    web_page: str = Field(...)