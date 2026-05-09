from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

# --- EMBEDDING MODEL ---
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# --- PDF LIST ---
PDF_SOURCES = [
    {
      "path": "data/CS_Department_Catalog.pdf",
      "department": "Computer Science",
      "doc_type": "course_catalog",
      "course_level": "undergraduate_graduate"
    },
    {
      "path": "data/EE_Department_Catalog.pdf",
      "department": "Electrical Engineering",
      "doc_type": "course_catalog",
      "course_level": "undergraduate"
    },
    {
      "path": "data/BBA_Department_Catalog.pdf",
      "department": "Business Administration",
      "doc_type": "course_catalog",
      "course_level": "undergraduate"
    },
    {
      "path": "data/University_Academic_Policies.pdf",
      "department": "University",
      "doc_type": "academic_policy",
      "course_level": "all"
    },
    {
      "path": "data/Faculty_Directory.pdf",
      "department": "All",
      "doc_type": "faculty_directory",
      "course_level": "all"
    }
]

import shutil

def create_vector_store():
    """
    Creates a pure-Python vector store (pickle) to bypass ChromaDB/Python 3.14 crashes.
    """
    print("Initializing embeddings...")
    from langchain_huggingface import HuggingFaceEmbeddings
    embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    all_chunks = []
    # Increase size and overlap to keep headers with content
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=400,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    for source in PDF_SOURCES:
        if not os.path.exists(source["path"]):
            print(f"Warning: File not found {source['path']}")
            continue
            
        print(f"Processing: {source['path']}")
        loader = PyPDFLoader(source["path"])
        pages = loader.load()
        
        # Inject metadata directly into text to ensure context is never lost
        for doc in pages:
            prefix = f"[DEPARTMENT: {source['department']}] [DOC: {source['doc_type']}]\n"
            doc.page_content = prefix + doc.page_content
            
            doc.metadata["department"] = source["department"]
            doc.metadata["doc_type"] = source["doc_type"]
            doc.metadata["course_level"] = source["course_level"]
            doc.metadata["source_file"] = source["path"]
            
        chunks = splitter.split_documents(pages)
        all_chunks.extend(chunks)
        
    print(f"Embedding {len(all_chunks)} chunks (Pure Python)...")
    texts = [chunk.page_content for chunk in all_chunks]
    embeddings = embeddings_model.embed_documents(texts)
    
    db_path = "vector_store_fallback.pkl"
    import pickle
    with open(db_path, "wb") as f:
        pickle.dump({"chunks": all_chunks, "embeddings": embeddings}, f)
        
    print(f"Saved {len(all_chunks)} chunks to {db_path}")

if __name__ == "__main__":
    create_vector_store()
