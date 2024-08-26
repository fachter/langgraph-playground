from pydantic import BaseModel


class CoverLetterArguments(BaseModel):
    job_advert_url: str
