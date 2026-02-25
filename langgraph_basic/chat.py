from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    return { "message" : ["Hello, This is a message from chatbot model"]}

def samplenode(state: State):
    return { "message" : ["Sample message appended"]}

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("samplenode", chatbot)

graph_builder.add_edge(START,"chatbot")
graph_builder.add_edge("chatbot","samplenode")
graph_builder.add_edge("samplenode",END)

# (START) : chatbot -> samplenode -> (END)

#state = { messages : ["Hey There"]}
#node runs: chatbot(state: ["Hey There"]) -> ["Hi, There is a message from chatbot "]
#state = { "messages" : ["Hey There", "Hi, There is a message from chatbot "]}