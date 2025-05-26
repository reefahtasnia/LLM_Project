from openai import OpenAI
import chromadb
from sentence_transformers import SentenceTransformer
import os

# ---- Connect to LM Studio ----
client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"  # Any string works
)

# ---- Connect to ChromaDB ----
chroma_client = chromadb.PersistentClient(path=r"D:\LLM_Project\vector_db")
collection = chroma_client.get_collection(name="pdf_embeddings")

# ---- Load Embedding Model ----
embedding_model = SentenceTransformer('BAAI/bge-small-en-v1.5')  # Must match ingestion model

# ---- Function to Search PDFs ----
def search_pdfs(query, n_results=3):
    query_embedding = embedding_model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    return results["documents"][0], results["metadatas"][0]

# ---- Function to Ask LLM ----
def ask_llm(question):
    # Step 1: Search for relevant PDF chunks
    docs, metadata = search_pdfs(question)
    
    # Step 2: Build context with source/page info
    context = "\n\n".join([
        f"Source: {os.path.basename(m['source'])} | Page: {m['page']}\n{d}" 
        for d, m in zip(docs, metadata)
    ])
    
    # Step 3: Ask LLM to answer using the context
    try:
        response = client.chat.completions.create(
            model="llama-3.2-1b-instruct",  # Must match model name in LM Studio
            messages=[
                {"role": "system", "content": "Answer based on the provided context. Cite sources like [Source: filename.pdf, Page: x]."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
            ],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# ---- Example Usage ----
if __name__ == "__main__":
    question = "What is Machine Learning?"
    answer = ask_llm(question)
    print(f"Answer: {answer}")