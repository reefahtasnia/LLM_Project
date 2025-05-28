# LLM_Project

A local PDF question-answering system using LLMs, ChromaDB, and a Next.js frontend.

## Features
- Upload PDF files via the web UI (files are saved to the `pdfs/` folder and processed automatically)
- Ask questions about your PDF documents and get instant, source-cited answers
- All PDF content is embedded and stored in ChromaDB for fast retrieval
- Modern chat UI built with Next.js

## Usage

### 1. Start the Backend (Flask)
```powershell
python backend.py
```
- The backend runs on `http://localhost:5000`.
- It exposes `/ask` for questions and `/upload_pdf` for PDF uploads.

### 2. Start the Frontend (Next.js)
```powershell
cd chatbot
npm install
npm run dev
```
- The frontend runs on `http://localhost:3000`.

### 3. Uploading PDFs
- Use the upload button in the chat UI to add new PDFs.
- Uploaded PDFs are saved to the `pdfs/` folder and processed into ChromaDB automatically.
- PDFs and their embeddings are **not** pushed to git (see `.gitignore`).

### 4. Asking Questions
- Type your question in the chat box.
- The system will search the vector database for relevant PDF chunks and generate a source-cited answer using the LLM.

## File Structure
- `backend.py` — Flask backend for LLM and PDF endpoints
- `pdf_processor.py` — Handles PDF splitting, embedding, and ChromaDB storage
- `pdfs/` — Folder for all PDF files (ignored by git)
- `vector_db/` — ChromaDB persistent storage
- `chatbot/` — Next.js frontend app

## Notes
- All `.pdf` files and the `pdfs/` folder are ignored by git (see `.gitignore`).
- To keep the `pdfs/` folder in git, a `.gitkeep` file is used.
- Only metadata and code are versioned; document content is local only.

## Requirements
- Python 3.10+
- Node.js 18+
- See `requirements.txt` and `chatbot/package.json` for dependencies

---

_Last updated: May 28, 2025_