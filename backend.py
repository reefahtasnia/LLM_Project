from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import chromadb
from sentence_transformers import SentenceTransformer
import os
from pdf_processor import process_pdf

app = Flask(__name__)
CORS(app)

# Initialize once at startup
client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")
chroma_client = chromadb.PersistentClient(path=r"E:\LLM_Project\vector_db")
collection = chroma_client.get_collection(name="pdf_embeddings")
embedding_model = SentenceTransformer('BAAI/bge-small-en-v1.5')

def get_page_number(page_metadata):
    """Extract and format page number correctly"""
    try:
        if isinstance(page_metadata, str):
            page_num = int(page_metadata)
        else:
            page_num = int(page_metadata)
        return page_num + 1
    except (ValueError, TypeError):
        return 1

def search_pdfs(query, n_results=3):
    query_embedding = embedding_model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=n_results)
    return results["documents"][0], results["metadatas"][0]

def is_greeting(text):
    """Check if the text is a greeting"""
    greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings']
    return any(greeting in text.lower().strip() for greeting in greetings)

def is_help_request(text):
    """Check if the text is asking for help"""
    help_phrases = ['help', 'assist', 'support', 'can you help', 'need help']
    return any(phrase in text.lower() for phrase in help_phrases)

def is_how_are_you(text):
    """Check if the text is asking 'how are you'"""
    how_are_you = ['how are you', 'how r u', 'how are you doing', 'how do you do']
    return any(phrase in text.lower().strip() for phrase in how_are_you)


@app.route('/ask', methods=['POST'])
def ask():
    print("Received request to /ask endpoint") 
    data = request.json
    question = data['question'].strip()
    
    # Handle special cases first - before doing any PDF search
    if is_greeting(question):
        print("Detected greeting, returning simple response")
        return jsonify({
            "answer": "Hello! How can I assist you today?",
            "sources": []
        })
    
    if is_help_request(question) and len(question.split()) <= 3:
        print("Detected help request, returning simple response")
        return jsonify({
            "answer": "Sure! What do you need help with?",
            "sources": []
        })
    
    if is_how_are_you(question):
        print("Detected 'how are you' question, returning simple response")
        return jsonify({
            "answer": "I'm just a program, but thanks for asking! How can I assist you?",
            "sources": []
        })
    
    if not question.endswith('?'):
        print("Question does not end with '?', checking for common question words")
        # Check if it contains common question words
        if not any(word in question.lower() for word in ['what', 'how', 'why', 'when', 'where', 'explain', 'tell', 'describe']):
            print("No clear question detected, prompting user")
            return jsonify({
                "answer": "Please ask a specific question that ends in '?'.",
                "sources": []
            })
    
    # Check for very short non-questions
    if not question.endswith('?') and len(question.split()) <= 5 and not any(word in question.lower() for word in ['what', 'how', 'why', 'when', 'where', 'explain', 'tell', 'describe', 'sources', 'source']):
        print("No clear question detected, prompting user")
        return jsonify({
            "answer": "Ask any questions you want.",
            "sources": []
        })
    
    # Get relevant document chunks for actual questions
    docs, metadata = search_pdfs(question)
    print(f"Found {len(docs)} documents for question: {question}")
    
    # Format context with proper page numbers
    context = "\n\n".join([
        f"### Document Excerpt {i+1} ###\n"
        f"Content: {d}\n"
        f"Source: {os.path.basename(m['source'])} (Page {get_page_number(m['page'])})"
        for i, (d, m) in enumerate(zip(docs, metadata))
    ])
    
    # Create a clear list of sources for the AI to reference
    source_list = []
    for i, m in enumerate(metadata):
        filename = os.path.basename(m['source'])
        page = get_page_number(m['page'])
        source_list.append(f"{filename}, Page {page}")
    
    sources_text = "Available sources: " + " | ".join(source_list)
    
    # Improved system prompt that emphasizes citing sources
    system_prompt = f"""You are a knowledgeable research assistant specializing in answering questions based on provided document context.

MANDATORY CITATION RULES - MUST FOLLOW:
1. ALWAYS cite sources using this EXACT format: [Source: filename.pdf, Page X] 
2. Add citations immediately after EVERY claim, fact, or piece of information you provide
3. Multiple citations are required - cite after each major point
4. Use **bold** for key terms and bullet points for clarity
5. If information is not available in documents, state "Not specified in documents"
6. If question is unrelated to context, state "Question not related to provided documents"

{sources_text}

CITATION EXAMPLES:
- "**Medical imaging** includes X-rays and MRI scans [Source: medical.pdf, Page 3]. **CT scans** provide detailed cross-sectional images [Source: imaging.pdf, Page 7]."
- "The study found three main benefits: improved accuracy, faster processing, and reduced costs [Source: research.pdf, Page 12]."

REMEMBER: Every factual statement MUST have a citation [Source: filename.pdf, Page X]"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.2-1b-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
            ],
            max_tokens=600,
            temperature=0.3,
        )
        
        answer = response.choices[0].message.content
        print("Generated answer:", answer)
        
        # Check if AI included citations - if not, add a reminder
        if "[Source:" not in answer and "Not specified in documents" not in answer and "Question not related" not in answer:
            answer += f"\n\n**Sources:** {', '.join(source_list)}"
        
        # Format sources with proper page numbers
        formatted_sources = []
        for m in metadata:
            formatted_sources.append({
                "file": os.path.basename(m['source']), 
                "page": get_page_number(m['page'])
            })
        
        return jsonify({
            "answer": answer,
            "sources": formatted_sources
        })
        
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": "Failed to generate answer"}), 500

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    print("Received request to /upload_pdf endpoint")
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    save_path = os.path.join('pdfs', file.filename)
    file.save(save_path)
    
    try:
        success = process_pdf(save_path)
        if success:
            return jsonify({
                'message': f'File {file.filename} uploaded and processed successfully.',
                'filename': file.filename
            }), 200
        else:
            return jsonify({
                'message': f'File {file.filename} was already processed.',
                'filename': file.filename
            }), 200
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return jsonify({
            'error': f'Failed to process PDF: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)