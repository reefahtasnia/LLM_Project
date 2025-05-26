import chromadb
from sentence_transformers import SentenceTransformer

# Load database and model
client = chromadb.PersistentClient(path=r"D:\LLM_Project\vector_db")
collection = client.get_collection(name="pdf_embeddings")
model = SentenceTransformer('BAAI/bge-small-en-v1.5')

# Search for relevant chunks
def search_pdf(query_text, n_results=3):
    query_embedding = model.encode([query_text]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    return results["documents"][0], results["metadatas"][0]