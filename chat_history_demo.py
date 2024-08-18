import operator
from typing import List, Dict, Annotated, Sequence, Optional, Literal

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import (
    PydanticOutputParser,
    StrOutputParser,
)
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    HumanMessagePromptTemplate,
    PromptTemplate,
)
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import OllamaLLM
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START
from langgraph.graph import StateGraph
from pydantic.v1 import BaseModel


class ContentNotes(BaseModel):
    notes: Dict[str, List[str]]


State = Literal[
    "not started",
    "topic_generation",
    "q_a",
    "determine_finished",
    "compute_result",
    "finished",
]


class DemoState(BaseModel):
    topic: str
    current_state: State = "not started"
    original_content: Optional[ContentNotes]
    updated_content: Optional[ContentNotes]
    messages: Annotated[Sequence[BaseMessage], operator.add] = []


def main():
    rag = MyRAG()
    for event in rag.stream(
        DemoState(topic="Should Data Scientist also write API and backend code?")
    ):
        print(event)
    for event in rag.stream(
        {
            "messages": [
                HumanMessage(
                    "Let's add some notes about Machine Learning engineers, and which role they play in this topic!"
                )
            ]
        }
    ):
        print(event)
    # for event in rag.stream("Question 2"):
    #     print(event)
    # for event in rag.stream("Thank you"):
    #     print(event)
    print("DONE!")


class MyRAG:
    def __init__(self):
        builder = StateGraph(DemoState)
        builder.add_node("topic_generation", self.topic_generation)
        builder.add_node("q_a", self.q_a)
        builder.add_node("determine_finished", self.determine_finished)
        builder.add_node("compute_result", self.compute_result)

        # builder.set_entry_point("topic_generation")
        builder.add_edge(START, "topic_generation")
        builder.add_edge("topic_generation", "q_a")
        builder.add_edge("q_a", "determine_finished")
        builder.add_conditional_edges(
            "determine_finished",
            self.determine_finished,
            {False: "q_a", True: "compute_result"},
        )
        builder.set_finish_point("compute_result")
        # builder.add_edge("compute_result", END)
        memory = MemorySaver()
        self.graph = builder.compile(checkpointer=memory, interrupt_before=[])
        self.thread = {"configurable": {"thread_id": "1"}}

    def stream(self, data):
        for event in self.graph.stream(data, self.thread, stream_mode="values"):
            yield event

    def topic_generation(self, state: DemoState):
        print(self.graph.get_name())
        print("---topic_generation---")
        prompt_message = """
        You are an expert content generator. Please create notes about the topic {topic}.
        The notes should be structured in 3 or 4 groups with a title. Each group should contain a list of ideas that will be written for that group.
        You should not write any sentences yet. Only answer with the notes about the topic.
        The should be formatted in json style, such that it can be converted to a python dictionary.
          Everything should be placed under the root node "notes" in the json.
          No need for any text before or after the answer, to allow for automated conversion. 
        And example answer could look like this:
        {{
        "notes": {{
                "<group1>": ["<idea1>", "<idea2>", "<idea3>"],
                "<group2>": ["<idea3>", "<idea4>],
                "<group3>": ["<idea5>", "<idea6>", "<idea7>", "<idea8>"],   
            }}
        }}    
         """
        parser = PydanticOutputParser(pydantic_object=ContentNotes)
        # prompt = ChatPromptTemplate.from_template(prompt_message)
        prompt = ChatPromptTemplate(
            [
                HumanMessagePromptTemplate(
                    prompt=PromptTemplate.from_template(prompt_message)
                )
            ],
            partial_variables={"template_format": parser.get_format_instructions()},
        )
        model = OllamaLLM(model="llama3.1:8b", temperature=0.2)
        chain = prompt | model | parser
        answer = chain.invoke({"topic": state.topic})

        return {
            "original_content": answer,
            "current_state": self.graph.get_state(self.thread).next[0],
        }

    def prompt_engineer(self, state: DemoState):
        prompt_message = """
        You are an expert prompt engineer. Based on the following input, create a detailed and structured prompt for an AI agent:
    
        Input: "{input_description}"
        
        The prompt should include:
        1. Role: Clearly define the role the AI should take.
        2. Task: Describe the task the AI needs to perform.
        3. Guidelines: Any specific rules or considerations.
        4. Expected Output: Describe what the final output should look like.
        
        Ensure the prompt is clear, actionable, and optimized for the AI to perform well.
        Even if any of the 4 topics (Role, Task, Guidelines & Expected Output) is not directly included in the input,
        try to infer it from the given Input.
         """



    def q_a(self, state: DemoState):
        prompt_message = """
        You are an expert prompt engineer. Write a standalone prompt that can be understood without any additional information.
        The prompt you are writing should summarize the following notes and tell to write a short essay with a few paragraphs about these notes:
        {notes}
        
        The following messages from the chat history (if any exist so far) can overwrite the notes.  
        Of course, if messages are in conflict to one another, the latest message overwrites the previous ones. 
        
        You do NOT answer any of the question, but you are writing the prompt to create the essay 
         which combines the thoughts presented in the notes as well as in the messages. 
        Your answer should be without any text before of after the prompt. So, your output will look something like this:
        
        You are an expert content creator. Write an essay about ...
         """
        prompt_message = """
         I have the following notes:
        {notes}

        Please summarize the notes to a well written text. Use the messages, which are related to the notes, in order to change the summary.
        The result text should be a summary of all the notes where the content of the message will overwrite the original content from the note.
        Of course, if messages are in conflict to one another, the latest message overwrites the previous ones. 
          
        The final summary should be concise, clear, and integrate the notes naturally.
        """
        print("---q_a---")
        parser = StrOutputParser()
        messages = [
            SystemMessage(prompt_message),
            MessagesPlaceholder("chat_history"),
            MessagesPlaceholder("notes")
        ]
        # prompt = ChatPromptTemplate.from_messages(
        #     messages,
        # )
        prompt = PromptTemplate(
            template=prompt_message,
            input_variables=["chat_history", "notes"]
        )
        # prompt = ChatPromptTemplate(
        #     messages,
        #     # input_variables=["chat_history", "notes"]
        #     # partial_variables={"template_format": parser.get_format_instructions()},
        # )
        model = OllamaLLM(model="llama3.1:8b", temperature=0.05)
        chain = RunnablePassthrough(notes=lambda inputs: inputs["notes"]) | prompt | model | parser
        answer = chain.invoke(
            {
                "notes": "\n\n".join([title + ":\n - " + "\n - ".join(values) for title, values in state.original_content.notes.items()]),
                "chat_history": state.messages,
            }
        )
        return {
            "updated_content": answer,
        }

    def determine_finished(self, state: DemoState):
        print(self.graph.get_name())
        print("---determine_finished---")
        return True

    def compute_result(self, state: DemoState):
        print(self.graph.get_name())
        print("---compute_result---")
        return {}


if __name__ == "__main__":
    main()
