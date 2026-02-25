import dramatiq
from rag_dramatic.broker import broker

from openai import OpenAI
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore


client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

embedding_model = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://localhost:11434"
)

vector_db = QdrantVectorStore.from_existing_collection(
    embedding=embedding_model,
    url="http://localhost:6333",
    collection_name="learning_rag"
)


@dramatiq.actor(store_results=True)
def process_query(user_input: str):

    print(f"Processing query: {user_input}")

    search_results = vector_db.similarity_search(query=user_input)

    context = "\n\n".join([
        f"Page Content: {result.page_content}\n"
        f"Page Number: {result.metadata.get('page_label')}\n"
        f"File Location: {result.metadata.get('source')}"
        for result in search_results
    ])

    SYSTEM_PROMPT = f"""
    You are a helpfull AI Assitant who answers user based query based on the available
    context retrieved from a PDF file along with page_contents and page number.

    You should only ans the user brand based on the following context and navigate the user
    to open the right page number to know more.

    Context:
    {context}
    """

    response = client.chat.completions.create(
        # model="gemma2:2b",
        model="tinyllama",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]
    )

    result = response.choices[0].message.content

    print("Result:", result)

    return result