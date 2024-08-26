from typing import Any, Dict

from fastapi import Depends
from langchain_core.prompts import PromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph

from src.dtos.cover_letter_state import State
from src.services.llama_model import ChatOllamaModel
from src.use_cases.cover_letter_writer_use_case import CoverLetterWriterUseCase
from src.use_cases.cv_helper_use_case import CvHelperUseCase
from src.utils.prompts import get_prompt_engineer_prompt
from src.viewmodels.cover_letter_communication import CoverLetterCommunication


class CreateCoverLetterUseCase:
    def __init__(
        self,
        model: ChatOllamaModel = Depends(),
        cv_helper_user_case: CvHelperUseCase = Depends(),
        cover_letter_writer_use_case: CoverLetterWriterUseCase = Depends(),
    ):
        self._model = model
        self._cv_helper_use_case = cv_helper_user_case
        self._cover_letter_writer_use_case = cover_letter_writer_use_case
        self._graph = None
        self._thread = {}

    def initialize(self):
        builder = StateGraph(State)
        builder.add_node("summarize_job_advert", self.summarize_job_advert)
        # builder.add_node("summarize_additional_pages", summarize_additional_pages) # TODO: insert later
        # builder.add_node("combine_summarized_content", combine_summarize_content) # TODO: insert later
        builder.add_node("human_feedback", human_feedback)
        builder.add_node("summarize_notes", self.summarize_notes_with_history)
        builder.add_node("write_cover_letter", self.write_cover_letter)
        builder.add_node("determine_finished", self.determine_finished)
        builder.add_node("finish", self.finish)

        builder.add_edge("summarize_job_advert", "human_feedback")
        builder.add_edge("human_feedback", "summarize_notes")
        builder.add_edge("summarize_notes", "write_cover_letter")
        builder.add_edge("write_cover_letter", "determine_finished")
        builder.add_conditional_edges(
            "determine_finished",
            self.determine_finished,
            {False: "summarize_notes", True: "finish"}
        )
        memory = MemorySaver()

        builder.set_entry_point("summarize_job_advert")
        graph = builder.compile(
            checkpointer=memory, interrupt_before=["human_feedback"]
        )
        self._graph = graph
        self._graph.get_graph().draw_mermaid_png(output_file_path="graph.png")
        self._thread = {"configurable": {"thread_id": "1"}}

    def summarize_job_advert(self, state: State) -> Dict[str, Any]:
        # cv_helper_use_case = Depends(CvHelperUseCase)
        print("---summarize_job_advert---")
        requirements = self._cv_helper_use_case.summarize_job_advert(
            state.get("job_advert_url")
        )
        print("Got requirements")

        return {"generated_job_requirements": requirements, "state": "ongoing"}

    def summarize_notes_with_history(self, state: State):
        print("---summarize_notes---")
        print(state)
        prompt_text = get_prompt_engineer_prompt()
        prompt = PromptTemplate.from_template(prompt_text)
        chain = self._model.get_chain(prompt)
        answer = chain.invoke({"input_description"})

    def write_cover_letter(self, state: State):
        print("---write_cover_letter---")
        print(state)
        pass

    def determine_finished(self, state: State):
        print("---determine_finished---")
        print(self._thread)
        print(state)
        return True

    def finish(self, state: State):
        return

    async def run(self, content: CoverLetterCommunication):
        if content.state == "start":
            if not content.job_advert_url:
                raise Exception("When starting, a web url is required!")
            async for event in self._start(content.job_advert_url):
                yield event
        elif content.state == "continue":
            if not content.job_requirements:
                raise Exception("Job requirements are mandatory to continue!")
            async for event in self._continue(content.job_requirements):
                yield event

    async def _start(self, web_page: str):
        initial_input = {"job_advert_url": web_page}
        for event in self._graph.stream(
            initial_input, self._thread, stream_mode="values"
        ):
            yield event

    async def _continue(self, updated_requirements: Dict[str, Any]):
        self._graph.update_state(
            self._thread, {"updated_job_requirements": updated_requirements}
        )
        for event in self._graph.stream(
            None, self._thread, stream_mode="values"
        ):
            yield event


def summarize_additional_pages(state: State):
    print("---summarize_additional_pages---")
    print(state)
    pass


def combine_summarize_content(state: State):
    print("---combine_summarize_content---")
    print(state)
    pass



def human_feedback(state: State):
    print("---human_feedback---")
    print(state)
    pass
