from typing import Optional, List, Union

from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from pydantic.v1 import BaseModel


class ChatModelArguments(BaseModel):
    prompt: Union[PromptTemplate, ChatPromptTemplate]
    parser: Optional[Union[StrOutputParser, JsonOutputParser]]
    input_variables: Optional[List[str]]
