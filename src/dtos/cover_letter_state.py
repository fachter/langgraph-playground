from typing import TypedDict, List, Dict, Any, Literal

from typing_extensions import NotRequired


class State(TypedDict):
    state: Literal['start', 'ongoing', 'close']
    job_advert_url: str
    additional_web_pages: List[str]
    generated_job_requirements: NotRequired[Dict[str, Any]]
    updated_job_requirements: NotRequired[Dict[str, Any]]
    user_feedback: List[str]
