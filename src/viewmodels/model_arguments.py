from langchain_core.prompts import BaseChatPromptTemplate
from pydantic.v1 import BaseModel, Field


class ChatModelArguments(BaseModel):
    prompt: BaseChatPromptTemplate = Field(...)
