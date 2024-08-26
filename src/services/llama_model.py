from fastapi import Depends
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate, BasePromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import OllamaLLM

from src.viewmodels.model_arguments import (
    ChatModelArguments,
)


def get_model_temperature() -> float:
    return 0.1


class ChatOllamaModel:

    def __init__(self, temperature: int = Depends(get_model_temperature)):
        self._model = OllamaLLM(model="llama3.1:8b", temperature=temperature)

    def get_chain(self, prompt: BasePromptTemplate):
        chain = prompt | self._model | StrOutputParser()
        return chain

    def get_chain_with_context_input(self, model_arguments: ChatModelArguments):
        chain = (
            RunnablePassthrough.assign(
                context=lambda content: format_docs(content["context"])
            )
            | model_arguments.prompt
            | self._model
            | model_arguments.parser if model_arguments.parser is not None else StrOutputParser()
        )
        return chain

    def get_chain_without_input(self, model_arguments: ChatModelArguments):
        chain = model_arguments.prompt | self._model | StrOutputParser()
        return chain


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)
