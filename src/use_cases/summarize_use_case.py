from typing import Any, Dict, List

from fastapi import Depends
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.services.llama_model import ChatOllamaModel
from src.utils.prompts import get_summarize_prompt


class SummarizeUseCase:
    def __init__(self, model: ChatOllamaModel = Depends()):
        self._model = model

    def summarize(self, notes: Dict[str, Any], messages: List[str]):
        prompt_text = get_summarize_prompt()
        prompt = ChatPromptTemplate(
            [SystemMessage(prompt_text), MessagesPlaceholder("chat_history")]
        )
        chain = self._model.get_chain(prompt)
        answer = chain.invoke({"notes": str(notes), "chat_history": format_list(messages)})
        return answer


def format_list(messages: List[Any]) -> str:
    if len(messages) == 0:
        return ""
    "- " + "\n- ".join(messages)
