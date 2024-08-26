import logging
from typing import List

from fastapi import Depends
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import Html2TextTransformer
from langchain_core.documents import Document
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from src.entities.web_page_content import WebContent, encode_url
from src.repositories.vector_embeddings import get_embedding_model
from src.repositories.web_content_repository import WebContentRepository
from src.services.llama_model import ChatOllamaModel
from src.utils.prompts import get_job_advert_summarize_prompt
from src.viewmodels.model_arguments import ChatModelArguments


class CvHelperUseCase:
    def __init__(
        self,
        model: ChatOllamaModel = Depends(),
        web_page_repository: WebContentRepository = Depends(),
    ):
        self._model = model
        self._repo = web_page_repository

    def summarize_job_advert(self, job_advert_request_page: str):
        web_content = self._get_processed_web_content(job_advert_request_page)

        output_parser = PydanticOutputParser(pydantic_object=ChatModelArguments)
        # prompt = ChatPromptTemplate.from_template(get_job_advert_summarize_prompt(), format)
        prompt = PromptTemplate(template=get_job_advert_summarize_prompt(), input_variables=["context"],
                       partial_variables={"format_instructions": output_parser.get_format_instructions()})
        chain = self._model.get_chain_with_context_input(
            ChatModelArguments(prompt=prompt, parser=output_parser)
        )
        answer = chain.invoke(
            {
                "context": [
                    Document(page_content=content.page_content)
                    for content in web_content
                ]
            }
        )

        try:
            decoded_answer = eval(answer)
            return decoded_answer
        except SyntaxError as e:
            logging.error(e)
            raise e

    def _get_processed_web_content(self, job_advert_web_page) -> List[WebContent]:
        encoded_url = encode_url(job_advert_web_page)
        existing_content = self._repo.find_all_by_encoded_url(encoded_url)

        if len(existing_content) == 0:
            all_splits = _read_and_split_web_content(job_advert_web_page)
            embedding_model = get_embedding_model()
            all_embeddings = embedding_model.embed_documents(
                [doc.page_content for doc in all_splits]
            )
            existing_content = self._repo.insert_many(
                [
                    WebContent(
                        encoded_url=encoded_url,
                        url=job_advert_web_page,
                        page_content=split.page_content,
                        embeddings=embeddings,
                    )
                    for embeddings, split in zip(all_embeddings, all_splits)
                ]
            )

        return existing_content


def _read_and_split_web_content(web_page):
    loader = AsyncHtmlLoader(web_page)
    html = loader.load()
    html_transformer = Html2TextTransformer()
    data = html_transformer.transform_documents(html)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    all_splits = text_splitter.split_documents(data)
    return all_splits
