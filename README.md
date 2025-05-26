# PDF Chatbot with LLM Integration

A RAG (Retrieval-Augmented Generation) system that allows querying information from PDF documents using local LLMs through LM Studio.

## Features

- 📄 **PDF Processing**: Extract text from multiple PDFs
- 🔍 **Semantic Search**: Find relevant document sections
- 💬 **LLM Integration**: Local inference via LM Studio
- 🖥️ **Web Interface**: Clean React-based UI
- 📊 **Source Attribution**: Shows document references

## Tech Stack

### Backend
- Python 3.10+
- Flask (REST API)
- ChromaDB (Vector Database)
- Sentence Transformers (Embeddings)
- LM Studio (Local LLM)

### Frontend
- Next.js 14
- React Markdown
- Tailwind CSS

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- LM Studio (with model loaded)

### Backend Setup
```bash
git clone [https://github.com/yourusername/LLM_Project.git](https://github.com/reefahtasnia/LLM_Project.git)
cd LLM_Project/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run backend
python backend.py
