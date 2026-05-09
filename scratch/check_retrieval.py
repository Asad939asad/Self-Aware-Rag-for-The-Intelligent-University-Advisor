from ingest import get_retriever
import sys

def check_query(query):
    retriever = get_retriever()
    docs = retriever.invoke(query)
    print(f"\n--- Search results for: '{query}' ---\n")
    for i, doc in enumerate(docs):
        print(f"Result {i+1} (Source: {doc.metadata.get('source_file')}):")
        print(f"{doc.page_content}\n")
        print("-" * 50)

if __name__ == "__main__":
    teacher_query = "Farhan Qureshi"
    if len(sys.argv) > 1:
        teacher_query = sys.argv[1]
    check_query(teacher_query)
