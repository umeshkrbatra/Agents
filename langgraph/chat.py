from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

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

def samplenode(state: State):
    print("\n\nInside samplenode node",state)
    return { "message" : ["Sample message appended"]}

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("samplenode", samplenode)

graph_builder.add_edge(START,"chatbot")
graph_builder.add_edge("chatbot","samplenode")
graph_builder.add_edge("samplenode",END)

graph = graph_builder.compile()

update_state = graph.invoke({
    "messages": [HumanMessage(content="Hi, My name is Umesh Batra")]
})
# update_state = graph.invoke(State({"messages":["Hi, My name is Umesh Batra"]}))

# (START) : chatbot -> samplenode -> (END)

#state = { messages : ["Hey There"]}
#node runs: chatbot(state: ["Hey There"]) -> ["Hi, There is a message from chatbot "]
#state = { "messages" : ["Hey There", "Hi, There is a message from chatbot "]}