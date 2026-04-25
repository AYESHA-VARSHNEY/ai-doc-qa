import os
import litellm
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import DeterministicFakeEmbedding
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# LiteLLM ko errors ignore karne ke liye set kiya
litellm.set_verbose = False
vector_stores = {}

def get_model_and_provider(api_key: str):
    if api_key.startswith("gsk_"):
        # Purana name 'llama-3.1-70b-versatile' ki jagah 
        # 'groq/llama-3.3-70b-specdec' ya 'groq/llama3-8b-8192' use karein
        return "groq/llama-3.3-70b-versatile", api_key
    elif api_key.startswith("AIza"):
        return "gemini/gemini-1.5-flash", api_key
    elif api_key.startswith("sk-ant"):
        return "anthropic/claude-3-5-sonnet-20240620", api_key
    else:
        return "openai/gpt-4o-mini", api_key

def index_text(file_id: str, text: str, api_key: str = ""):
    # Embeddings ke liye hum free version use kar rahe takki key ka issue na ho
    embeddings = DeterministicFakeEmbedding(size=1536)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_text(text)
    docs = [Document(page_content=c) for c in chunks]
    vs = FAISS.from_documents(docs, embeddings)
    vector_stores[file_id] = vs
    return True

def query_document(file_id: str, question: str, api_key: str = "") -> str:
    if file_id not in vector_stores:
        return "Document not indexed yet."
    
    model, key = get_model_and_provider(api_key)
    vs = vector_stores[file_id]
    docs = vs.similarity_search(question, k=3)
    context = "\n".join([d.page_content for d in docs])
    
    prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    
    response = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        api_key=key
    )
    return response.choices[0].message.content

def summarize_text(text: str, api_key: str = "") -> str:
    model, key = get_model_and_provider(api_key)
    prompt = f"Summarize the following content in 5-7 bullet points:\n\n{text[:4000]}"
    
    response = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        api_key=key
    )
    return response.choices[0].message.content