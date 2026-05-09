from langchain.tools import tool
from pydantic import BaseModel, Field
from langchain_community.tools.tavily_search import TavilySearchResults
import os
from dotenv import load_dotenv
import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

# Initialize embeddings once
embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# --- TOOL 1: retrieve_documents ---

class RetrieveInput(BaseModel):
    query: str = Field(description="The user's question to search for in the university knowledge base")

@tool(args_schema=RetrieveInput)
def retrieve_documents(query: str, k: int = 15) -> list[dict]:
    """
    Retrieves relevant document chunks using Python 3.14 safe similarity search.
    """
    import pickle
    db_path = "vector_store_fallback.pkl"
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found.")
        return []

    with open(db_path, "rb") as f:
        data = pickle.load(f)
        
    chunks = data["chunks"]
    chunk_embeddings = np.array(data["embeddings"])
    
    # Embed the query
    query_embedding = np.array(embeddings_model.embed_query(query))
    
    # Calculate cosine similarity: (A . B) / (||A|| * ||B||)
    dot_products = np.dot(chunk_embeddings, query_embedding)
    norms_chunks = np.linalg.norm(chunk_embeddings, axis=1)
    norm_query = np.linalg.norm(query_embedding)
    similarities = dot_products / (norms_chunks * norm_query)
    
    # Get top k indices
    top_indices = np.argsort(similarities)[::-1][:k]
    
    results = []
    for idx in top_indices:
        results.append({
            "content": chunks[idx].page_content,
            "metadata": chunks[idx].metadata
        })
    return results

# --- TOOL 2: web_search ---

class WebSearchInput(BaseModel):
    query: str = Field(description="Search query for finding information on the web when the knowledge base does not have the answer")

@tool(args_schema=WebSearchInput)
def web_search(query: str) -> list[dict]:
    """
    Performs a web search using Tavily to find information not available in the 
    university's internal knowledge base. Use this as a FALLBACK tool only when 
    all retrieved documents from the knowledge base were graded as irrelevant.
    Returns a list of web search results with title, content, and URL.
    """
    search = TavilySearchResults(max_results=3, tavily_api_key=os.getenv("TAVILY_API_KEY"))
    results = search.invoke(query)
    return results
