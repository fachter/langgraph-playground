import operator
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.constants import START
from langgraph.graph import StateGraph, END
from pydantic.v1 import BaseModel

from src.repositories import connection_string


class MyState(BaseModel):
    step: int = 0
    messages: Annotated[Sequence[BaseMessage], operator.add] = []


def start_step(_state: MyState):
    print("---Step 1---")
    return {"step": 1}


def display_step(state: MyState):
    print("---Step 2---")
    return {
        "step": 2,
        "messages": [AIMessage(f"There are currently {len(state.messages)} messages!")],
    }


def human_in_the_loop(_state: MyState):
    print("---Human In The Loop---")
    return {"step": 3}


def determine_finished(state: MyState):
    print("---Should Finish---")
    if len(state.messages) == 0 or "END" != state.messages[-1].content:
        return False
    return True

def last_step(state: MyState):
    print("---Last Step---")
    print(state)
    return {"step": state.step + 1}


def get_checkpointer():
    with PostgresSaver.from_conn_string(connection_string) as checkpointer:
        yield checkpointer

def main():
    graph_builder = StateGraph(MyState)
    graph_builder.add_node("start", start_step)
    graph_builder.add_node("display", display_step)
    graph_builder.add_node("human_in_the_loop", human_in_the_loop)
    graph_builder.add_node("last_step", last_step)

    graph_builder.set_entry_point("start")
    graph_builder.add_edge("start", "display")
    graph_builder.add_edge("display", "human_in_the_loop")
    graph_builder.add_conditional_edges(
        "human_in_the_loop", determine_finished, {False: "display", True: "last_step"}
    )
    graph_builder.add_edge("last_step", END)
    with PostgresSaver.from_conn_string(connection_string) as checkpointer:
        checkpointer.setup()
        my_graph = graph_builder.compile(
            interrupt_before=["human_in_the_loop"], checkpointer=checkpointer
        )
        thread_config = {"configurable": {"thread_id": "2"}}

        for event in my_graph.stream({"step": -1}, thread_config, stream_mode="values"):
            print(event)

        for event in my_graph.stream(
                {"messages": [HumanMessage("This will restart the graph from first step")]}, # ALWAYS PASS NONE and update state before
                thread_config,
                stream_mode="values",
        ):
            print(event)
        my_graph.update_state(thread_config, {"messages": [HumanMessage("This will continue in step 2")]})
        for event in my_graph.stream(
            None,
            thread_config,
            stream_mode="values",
        ):
            print(event)
        my_graph.update_state(thread_config, {"messages": [HumanMessage("END")]})
        for event in my_graph.stream(
            None, thread_config, stream_mode="values"
        ):
            print(event)
        print(my_graph.get_state(thread_config))


class State(TypedDict):
    input: str


def step_1(_state):
    print("---Step 1---")
    pass


def step_2(_state):
    print("---Step 2---")
    pass


def step_3(_state):
    print("---Step 3---")
    pass


def langgraph_example():
    initial_input = {"input": "hello world"}
    builder = StateGraph(State)
    builder.add_node("step_1", step_1)
    builder.add_node("step_2", step_2)
    builder.add_node("step_3", step_3)
    builder.add_edge(START, "step_1")
    builder.add_edge("step_1", "step_2")
    builder.add_edge("step_2", "step_3")
    builder.add_edge("step_3", END)
    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory, interrupt_before=["step_3"])

    # Thread
    thread = {"configurable": {"thread_id": "1"}}

    # Run the graph until the first interruption
    for event in graph.stream(initial_input, thread, stream_mode="values"):
        print(event)

    user_approval = input("Do you want to go to Step 3? (yes/no): ")

    if user_approval.lower() == "yes":
        # If approved, continue the graph execution
        for event in graph.stream(None, thread, stream_mode="values"):
            print(event)
    else:
        print("Operation cancelled by user.")


if __name__ == "__main__":
    main()
    # langgraph_example()
