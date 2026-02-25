from mem0 import Memory
from openai import OpenAI
import json

config = {
    "version": "v1.1",
    "embedder": {
        "provider": "ollama",
        "config": {"model": "nomic-embed-text"}
    },
    "llm": {
        "provider": "ollama",
        "config": {"model": "tinyllama","temperature": 0.1}
    },
    "vector_store":{
        "provider": "qdrant",
        "config": {
            "host": "localhost", 
            "port": 6333
        }
    }
}

client = OpenAI(
    base_url = "http://localhost:11434/v1",
    api_key = "ollama"
)

mem_client = Memory.from_config(config)


while True:
    user_query = input("Enter your query : ")

    search_memory = mem_client.search(query=user_query,user_id= "umesh")

    memories = [
        f"ID: {mem.get("id")}\nMemory: {mem.get("memory")}" for mem in search_memory.get("results")
    ]

    print("Memories Found", memories)

    SYSTEM_PROMPT = f"""
        Here is the context about the user:
        {json.dumps(memories)}
    """

    response =client.chat.completions.create(
        # model="gemma2:2b",
        model="tinyllama",
        messages= [
            {"role":"System", "content": SYSTEM_PROMPT},
            {"role":"User", "content": user_query}
        ]
    )

    ai_response =  response.choices[0].message.content

    print(ai_response)

    mem_client.add(
        user_id= "umesh",
        messages=[
            {"role":"user","content":user_query},
            {"role":"assistant","content":ai_response}
        ]
    )