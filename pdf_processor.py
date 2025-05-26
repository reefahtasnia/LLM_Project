from langchain_community.document_loaders import PyPDFLoader  
from langchain.text_splitter import CharacterTextSplitter    
from sentence_transformers import SentenceTransformer          
import chromadb                                              
import os                                                    

# ---- SETTINGS ----
pdf_folder = r"D:\LLM_Project\pdfs"          
vector_db_path = r"D:\LLM_Project\vector_db"  

# ---- CHECK PDF FOLDER ----
if not os.path.exists(pdf_folder):
    print(f"❌ PDF folder not found: {pdf_folder}")
    exit()
else:
    print(f"✅ PDF folder found at: {pdf_folder}")

# ---- CONNECT TO CHROMA DB ----
client = chromadb.PersistentClient(path=vector_db_path)  
collection = client.get_or_create_collection(name="pdf_embeddings")  


# ---- GET EXISTING SOURCES ----
# Fetch all items (default limit is 10, so set a high limit)
existing_data = collection.get(include=["metadatas"], limit=1000000)
# Extract full source paths from metadata
existing_sources = [item["source"] for item in existing_data["metadatas"]]
# Store full paths for exact match
existing_files = set(existing_sources)

# ---- LOAD ONLY NEW PDFs ----
all_documents = []
for filename in os.listdir(pdf_folder):
    if filename.lower().endswith(".pdf"):
        file_path = os.path.join(pdf_folder, filename)
        # Normalize path format (Windows/Linux compatibility)
        file_path = os.path.normpath(file_path)

        # Skip if already in ChromaDB
        if file_path in existing_files:
            print(f"📄 PDF already exists in Chroma: {filename}")
            continue

        # Load new PDF
        print(f"📄 Processing new PDF: {filename}")
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        all_documents.extend(documents)


if not all_documents:
    print("✅ No new PDFs to process")
    exit()


# ---- SPLIT TEXT INTO CHUNKS ----
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(all_documents)
print(f"✅ Split into {len(chunks)} chunks")

# ---- GENERATE EMBEDDINGS ----
model = SentenceTransformer('BAAI/bge-small-en-v1.5')
embeddings = [model.encode(chunk.page_content).tolist() for chunk in chunks]

# ---- SAVE METADATA ----
metadata = [
    {"source": chunk.metadata["source"], "page": str(chunk.metadata["page"])}
    for chunk in chunks
]

# ---- ADD TO CHROMA DB ----
collection.add(
    embeddings=embeddings,
    metadatas=metadata,
    documents=[chunk.page_content for chunk in chunks],
    ids=[f"id_{i}" for i in range(len(embeddings))]
)

print(f"✅ New embeddings saved to ChromaDB at {vector_db_path}")