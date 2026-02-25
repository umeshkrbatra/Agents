from langgraph.graph import StateGraph, START, END
from typing import Optional, Literal
from typing_extensions import TypedDict
from openai import OpenAI


client = OpenAI(
    base_url = "http://localhost:11434/v1",
    api_key = "ollama"
)

class State(TypedDict):
    user_query: str
    llm_output: Optional[str]
    is_good: Optional[bool]

def chatbot(state: State):
    response = client.chat.completions.create(
        model="gemma2:2b",
        messages=[
            {"role":"user","content":state.get("user_query")}
        ]
    )

    state["llm_output"] = response.choices[0].message.content
    return state


def evaluate_response(state:State) -> Literal['evaluate_ollama', "endnode"]:
    if True:
        return "endnode"

    return "evaluate_ollama"    


def evaluate_ollama(state:State):
    response = client.chat.completions.create(
        # model="gemma2:2b",
        model="tinyllama",
        messages=[
            {"role":"user","content":state.get("user_query")}
        ]
    )

    state["llm_output"] = response.choices[0].message.content
    return state


def endnode(state:State):
    return state

graphbuilder = StateGraph(State)
graphbuilder.add_node("chatbot",chatbot)
graphbuilder.add_node("evaluate_ollama",evaluate_ollama)
graphbuilder.add_node("endnode",endnode)

graphbuilder.add_edge(START, "chatbot")
graphbuilder.add_conditional_edges("chatbot", evaluate_response)
graphbuilder.add_edge("evaluate_ollama", "endnode")
graphbuilder.add_edge("endnode", END)

graph = graphbuilder.compile()

updated_graph = graph.invoke(State({"user_query":"What is 2+2 ?"}))
print(updated_graph)