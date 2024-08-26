from fastapi import Depends

from src.services.llama_model import ChatOllamaModel


class CoverLetterWriterUseCase:
    def __init__(self, model: ChatOllamaModel = Depends()):
        self._model = model

