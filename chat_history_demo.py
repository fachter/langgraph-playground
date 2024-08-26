import io
import operator
from typing import List, Dict, Annotated, Sequence, Optional, Literal

import PIL.Image as Image
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.output_parsers import (
    PydanticOutputParser,
    StrOutputParser,
)
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
)
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
    blog_prompt: Optional[str] = None
    draft: Optional[str] = None
    # updated_content: Optional[ContentNotes]
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
        builder.add_node("blog_prompt_engineer", self.prompt_engineer)
        builder.add_node("blog_writer", self.blog_writer)
        builder.add_node("determine_finished", self.determine_finished)
        builder.add_node("compute_result", self.compute_result)

        # builder.set_entry_point("topic_generation")
        builder.add_edge(START, "topic_generation")
        builder.add_edge("topic_generation", "blog_prompt_engineer")
        builder.add_edge("blog_prompt_engineer", "blog_writer")
        builder.add_edge("blog_writer", "determine_finished")
        builder.add_conditional_edges(
            "determine_finished",
            self.determine_finished,
            {False: "blog_prompt_engineer", True: "compute_result"},
        )
        builder.set_finish_point("compute_result")
        # builder.add_edge("compute_result", END)
        self._memory = MemorySaver()
        self.graph = builder.compile(
            checkpointer=self._memory,
            interrupt_before=[],
            interrupt_after=["blog_writer"],
        )
        self.thread = {"configurable": {"thread_id": "1"}}
        self._model = OllamaLLM(model="llama3.1:8b", temperature=0.2)

    async def invoke(self, data):
        return self.graph.invoke(data, self.thread)
        # return await self.graph.ainvoke(data, config=self.thread)

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
        chain = prompt | self._model | parser
        answer = chain.invoke({"topic": state.topic})

        return {
            "original_content": answer,
            "current_state": self.graph.get_state(self.thread).next[0],
        }

    def prompt_engineer(self, state: DemoState):
        prompt_engineer_prompt = """
         You are an expert prompt engineer. Based on the following notes as well as the message history,
           create a detailed and structured prompt for an AI agent:
         
         Topic: {topic}
         Notes: {notes}
         Message History: {chat_history} 
         
         The prompt should include:
         1. Role: A blog poster
         2. Task: The task is to write a blog about the topic mentioned in the notes.
         3. Guidelines: Any specific rules or considerations.
         4. Content: The content of the blog will be the summary of the notes and the chat history. 
         5. Expected Output: The final output should be a blog ready to be published.
         
         Ensure the prompt is clear, actionable, and optimized for the AI to perform well.
         Summarize the notes, such that the prompt can be understood without additional information.
         These notes provide information about a topic. The prompt should include all these information,
           such that an AI agent receiving the prompt can understand it. 
           The messages from the chat history will be additional information on top of the notes.
           Use them to adjust or overwrite the notes, such that the resulting prompt will contain all the information how the content of the blog should look like.
           If the content of messages conflicts with one another (or with the original notes), use the latest content as truth. 
         If a message says that something from the notes should not be mentioned, don't mention it at all in the summary.
         You should NOT say that the AI agent shouldn't mention it, but YOU should NOT mention it in the first place.   
            
         Do NOT write the blog. You should write the prompt for the next agent, who will write a blog with the information that you will provide.
           
         --------------
         Example:
         Notes: {{
         "topic": "home office vs office" 
         "pros": ["no time required to go to work", "take care of your children"]
         "cons": ["more time spend at home", ""]
         }}
         Chat History: 
         - Human: Don't mention that you can take care of your children
         - Human: Also mention that you don't see you colleagues as a con 
         
         Example Output:
         "You are a professional blog poster. Your task is to write a blog which fits well to the following content:
         The topic is Home Office vs Office. Pros for home office are that you do not need time to go to work.
         As cons you have that you need to spend more time at home. Also, you don't get to see your colleagues in person. 
         Write the blog that is covering both sides. Don't make anything other arguments up, only stick to the presented ones.
         
         Guidelines:
         - Do not make anything up
         - Use clear and concise language
         
         Expected Output: The final output should be a blog post
         - Mentioning the pros and cons of working in the home office compared to the office
         - The overall length of the blog post should be less than a page, structured in a few paragraphs.
         "
         --------------
         
         Don't write any additional text before or after the prompt. Just the prompt is fine.
          Also, formulate it as if you were talking to the AI agent and write whole sentences.
          For example a start of your result could look like this. "You are a professional blog post writer..."   
         """
        # prompt_message = prompt_engineer_prompt
        # # prompt = PromptTemplate.from_template(prompt_message)
        # prompt = ChatPromptTemplate.from_messages([
        #     SystemMessage(prompt_message),
        #     MessagesPlaceholder("chat_history")
        # ])
        prompt = PromptTemplate.from_template(prompt_engineer_prompt)
        chain = prompt | self._model | StrOutputParser()
        answer = chain.invoke(
            {
                "topic": state.topic,
                "notes": str(state.original_content.notes),
                "chat_history": state.messages,
            }
        )
        return {"blog_prompt": answer}

    def blog_writer(self, state: DemoState):
        print("---blog_writer---")
        answer = self._model.invoke(state.blog_prompt)
        return {
            "draft": answer,
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
