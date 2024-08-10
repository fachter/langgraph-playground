from typing import List

from fastapi import Depends
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PlaywrightURLLoader,
)
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from src.entities.web_page_content import WebContent, encode_url
from src.repositories.vector_embeddings import get_embedding_model
from src.repositories.web_content_repository import WebContentRepository
from src.services.llama_model import ChatOllamaModel
from src.utils.prompts import get_job_advert_summarize_prompt
from src.viewmodels.job_advert_request import JobAdvertRequest
from src.viewmodels.model_arguments import ChatModelArguments


class CvHelperUseCase:
    def __init__(
        self,
        model: ChatOllamaModel = Depends(),
        web_page_repository: WebContentRepository = Depends(),
    ):
        self._model = model
        self._repo = web_page_repository

    def summarize_job_advert(self, job_advert_request: JobAdvertRequest):
        web_content = self._get_processed_web_content(job_advert_request)

        prompt = ChatPromptTemplate.from_template(get_job_advert_summarize_prompt())
        chain = self._model.get_chain(ChatModelArguments(prompt=prompt))
        answer = chain.invoke({"context": [
            Document(page_content=content.page_content) for content in web_content
        ]})

        try:
            decoded_answer = eval(answer)
        except SyntaxError:
            print("Invalid LLM Answer that could not be processed to python dict")
            decoded_answer = answer
        return decoded_answer

    def _get_processed_web_content(self, job_advert_request) -> List[WebContent]:
        encoded_url = encode_url(job_advert_request.web_page)
        existing_content = self._repo.find_all_by_encoded_url(encoded_url)

        if len(existing_content) == 0:
            all_splits = _read_and_split_web_content(job_advert_request)
            embedding_model = get_embedding_model()
            all_embeddings = embedding_model.embed_documents(
                [doc.page_content for doc in all_splits]
            )
            existing_content = self._repo.insert_many(
                [
                    WebContent(
                        encoded_url=encoded_url,
                        url=job_advert_request.web_page,
                        page_content=split.page_content,
                        embeddings=embeddings,
                    )
                    for embeddings, split in zip(all_embeddings, all_splits)
                ]
            )

        return existing_content


def _read_and_split_web_content(job_advert_request):
    loader = PlaywrightURLLoader([job_advert_request.web_page])
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    all_splits = text_splitter.split_documents(data)
    return all_splits
