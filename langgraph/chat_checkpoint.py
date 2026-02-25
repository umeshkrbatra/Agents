from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.mongodb import MongoDBSaver

llm = init_chat_model(
    # model="gemma2:2b",
    model="tinyllama",
    model_provider="ollama"
)

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    response = llm.invoke(state.get("messages"))
    return { "messages" : [response]}
    # return { "messages" : ["Hello, This is a message from chatbot model"]}

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START,"chatbot")
graph_builder.add_edge("chatbot",END)

graph = graph_builder.compile()

def compile_graph_with_checkpointer(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)

DB_URI = "mongodb://admin:admin@localhost:27017"
with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
    graph_with_checkpointer = compile_graph_with_checkpointer(checkpointer=checkpointer)
    

    config = {
    "configurable" : {
        "thread_id": "umesh"
    }
    }
    # update_state = graph_with_checkpointer.invoke(State({"messages":["Hi, My name is Umesh Batra"]}),
    #                                           config,)

    # update_state = graph_with_checkpointer.invoke(State({"messages":["What is my name ?"]}),
    #                                           config,)    
    
    # print(update_state)

    graph_with_checkpointer.invoke(
        {
            "messages": [
                HumanMessage(content="Hi, My name is Umesh Batra")
            ]
        },
        config
    )

    # graph_with_checkpointer.invoke(
    #     {
    #         "messages": [
    #             HumanMessage(content="What is my name?")
    #         ]
    #     },
    #     config
    # )

    for chunk in graph_with_checkpointer.stream(
        {
            "messages": [
                HumanMessage(content="What is my name?")
            ]
        },
        config,
        stream_mode="values"
    ):
        chunk["messages"][-1].pretty_print()
    

    # for chunk in graph_with_checkpointer.stream(
    #     State({"messages":["What is my name ?"]}),
    #     config,
    #     stream_mode="values"
    #     ):
    #         chunk["messages"][-1].pretty_print()







# update_state = graph_with_checkpointer.invoke({
#     "messages": [HumanMessage(content="Hi, My name is Umesh Batra")]
# })


# (START) : chatbot -> (END)

#state = { messages : ["Hey There"]}
#node runs: chatbot(state: ["Hey There"]) -> ["Hi, There is a message from chatbot "]
#state = { "messages" : ["Hey There", "Hi, There is a message from chatbot "]}

# checkpointer (umesh) = Hey, My name is umesh batra