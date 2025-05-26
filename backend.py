from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import chromadb
from sentence_transformers import SentenceTransformer
import os

app = Flask(__name__)
CORS(app)

# Initialize once at startup
client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")
chroma_client = chromadb.PersistentClient(path=r"D:\LLM_Project\vector_db")
collection = chroma_client.get_collection(name="pdf_embeddings")
embedding_model = SentenceTransformer('BAAI/bge-small-en-v1.5')

def search_pdfs(query, n_results=3):
    query_embedding = embedding_model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=n_results)
    return results["documents"][0], results["metadatas"][0]


@app.route('/ask', methods=['POST'])
def ask():
    print("Received request to /ask endpoint") 
    data = request.json
    
    # Get relevant document chunks
    docs, metadata = search_pdfs(data['question'])
    print(f"Found {len(docs)} documents for question: {data['question']}")
    
    # Format context
    context = "\n\n".join([
        f"### Document Excerpt {i+1} ###\n"
        f"Content: {d}\n"
        f"Source: {os.path.basename(m['source'])} (Page {m['page']})"
        for i, (d, m) in enumerate(zip(docs, metadata))
    ])
    
    system_prompt = """You are a research assistant. Rules:
    - Answer ONLY using the provided context
    - Use bullet points and **bold** key terms
    - Cite sources as [Source: filename.pdf, Page X]
    - If unsure, say "Not specified in documents"
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.2-1b-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context}\nQuestion: {data['question']}"}
            ],
            max_tokens=400,  
            temperature=0.7,
        )
        
        answer = response.choices[0].message.content
        print("Generated answer:", answer)
        print("sources:", metadata)
        return jsonify({
            "answer": answer,
            "sources": [{"file": os.path.basename(m['source']), "page": m['page']} for m in metadata]
        })
        
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": "Failed to generate answer"}), 500

if __name__ == '__main__':
    # Run with: python backend.py
    print("Starting Flask app...")
    app.run(host='0.0.0.0', port=5000, threaded=True)