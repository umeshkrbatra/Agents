from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI
#from dotenv import load_dotenv

#load_dotenv()

client = OpenAI(
    base_url = "http://localhost:11434/v1",
    api_key = "ollama"
)


pdf_path = Path(__file__).parent / "Annual-Report.pdf" 
#pdf_path = Path(__name__).parent / "Annual-Report.pdf"

# Load the pdf file
loader = PyPDFLoader(pdf_path) 
docs = loader.load()
print(docs[12])

#Split the docs into the smaller chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 400
)

chunks = text_splitter.split_documents(documents=docs)

#Vector Embedding
# embedding_model = OpenAIEmbeddings(
#     model = "text-embedding-3-large",
# )

# Vector Embedding - Use the native Ollama class

embedding_model = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://localhost:11434" 
)

vectore_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedding_model,
    url="http://localhost:6333",
    collection_name="learning_rag" 
)

print('Rag Indexing done')