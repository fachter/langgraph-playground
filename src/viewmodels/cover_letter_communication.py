from typing import Literal, Optional, Any, Dict

from pydantic import BaseModel


class CoverLetterCommunication(BaseModel):
    state: Literal['start', 'ongoing', 'close'] = 'start'
    job_advert_url: Optional[str] = None
    job_requirements: Optional[Dict[str, Any]] = None
