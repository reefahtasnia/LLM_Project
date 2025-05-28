from langchain_community.document_loaders import PyPDFLoader  
from langchain.text_splitter import CharacterTextSplitter    
from sentence_transformers import SentenceTransformer          
import chromadb                                              
import os                                                    

# ---- SETTINGS ----
pdf_folder = r"E:\LLM_Project\pdfs"          
vector_db_path = r"E:\LLM_Project\vector_db"  

class PDFVectorDB:
    # Initialize the PDFVectorDB with ChromaDB client and collection
    # If I need to change anything initialized then I can do it here
    # self: means this class instance
    def __init__(self, vector_db_path=vector_db_path):
        self.vector_db_path = vector_db_path
        self.client = chromadb.PersistentClient(path=vector_db_path)
        self.collection = self.client.get_or_create_collection(name="pdf_embeddings")
        self.text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        self.model = SentenceTransformer('BAAI/bge-small-en-v1.5')
    
    def get_existing_sources(self):
        # Get existing sources from ChromaDB
        existing_data = self.collection.get(include=["metadatas"], limit=1000000)
        existing_sources = [item["source"] for item in existing_data["metadatas"]]
        return set(existing_sources)
    
    def get_next_id_start(self):
        """
        Retrieves the next available numeric ID by scanning existing document IDs in the collection.
        Returns the next integer to use as an ID, ensuring no conflicts with current IDs.
        If no IDs are found or an error occurs, returns 0.
        """
        try:
            all_data = self.collection.get(include=["documents"])
            if all_data["ids"]:
                existing_ids = []
                for id_str in all_data["ids"]:
                    if id_str.startswith('id_'):
                        try:
                            num = int(id_str.split('_')[1])
                            existing_ids.append(num)
                        except (IndexError, ValueError):
                            continue
                if existing_ids:
                    return max(existing_ids) + 1
                else:
                    return 0
            return 0
        except:
            return 0
    
    def add_documents_to_db(self, chunks, id_start=None):
        # Add document chunks to ChromaDB
        if id_start is None:
            id_start = self.get_next_id_start()
            
        # ---- GENERATE EMBEDDINGS ----
        embeddings = [self.model.encode(chunk.page_content).tolist() for chunk in chunks]

        # ---- SAVE METADATA WITH PROPER PAGE NUMBERS ----
        metadata = []
        for chunk in chunks:
            # Store page numbers as integers (keeping 0-based for internal consistency)
            # The frontend will handle converting to 1-based display
            page_num = chunk.metadata.get("page", 0)
            if isinstance(page_num, str):
                try:
                    page_num = int(page_num)
                except ValueError:
                    page_num = 0
            
            metadata.append({
                "source": chunk.metadata["source"], 
                "page": page_num  # Keep as integer, not string
            })

        # ---- ADD TO CHROMA DB ----
        self.collection.add(
            embeddings=embeddings,
            metadatas=metadata,
            documents=[chunk.page_content for chunk in chunks],
            ids=[f"id_{i + id_start}" for i in range(len(embeddings))]
        )
        return True

def check_pdf_folder():
    """Check if PDF folder exists"""
    if not os.path.exists(pdf_folder):
        print(f"❌ PDF folder not found: {pdf_folder}")
        return False
    else:
        print(f"✅ PDF folder found at: {pdf_folder}")
        return True

def load_and_split_pdf(file_path):
    """Load and split a single PDF"""
    print(f"📄 Processing PDF: {os.path.basename(file_path)}")
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    # Debug: Print page information
    print(f"📊 PDF loaded with {len(documents)} pages")
    for i, doc in enumerate(documents[:3]):  # Show first 3 pages for debugging
        print(f"  Page {i}: metadata = {doc.metadata}")
    
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)
    print(f"✅ Split into {len(chunks)} chunks")
    
    # Debug: Print chunk information
    print(f"📊 Sample chunk metadata:")
    for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks for debugging
        print(f"  Chunk {i}: page = {chunk.metadata.get('page', 'Unknown')}, source = {os.path.basename(chunk.metadata.get('source', 'Unknown'))}")
    
    return chunks

def process_pdf(file_path: str):
    """Process a single PDF"""
    # ---- CONNECT TO CHROMA DB ----
    db = PDFVectorDB()

    # ---- CHECK IF PDF ALREADY EXISTS ----
    existing_sources = db.get_existing_sources()
    normalized_path = os.path.normpath(file_path)
    
    if normalized_path in existing_sources:
        print(f"📄 PDF already exists in Chroma: {os.path.basename(file_path)}")
        return False

    # ---- PROCESS NEW PDF ----
    chunks = load_and_split_pdf(file_path)
    
    # ---- ADD TO CHROMA DB ---- 
    db.add_documents_to_db(chunks)

    print(f"✅ PDF processed successfully: {os.path.basename(file_path)}")
    return True

def process_all_pdfs():
    """Process all PDFs in folder and add to ChromaDB"""
    # ---- CHECK PDF FOLDER ----
    if not check_pdf_folder():
        exit()

    # ---- CONNECT TO CHROMA DB ----
    db = PDFVectorDB()

    # ---- GET EXISTING SOURCES ----
    existing_files = db.get_existing_sources()

    # ---- LOAD ONLY NEW PDFs ----
    all_documents = []
    for filename in os.listdir(pdf_folder):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(pdf_folder, filename)
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
        return

    # ---- SPLIT TEXT INTO CHUNKS ----
    chunks = db.text_splitter.split_documents(all_documents)
    print(f"✅ Split into {len(chunks)} chunks")

    # ---- ADD TO CHROMA DB ----
    db.add_documents_to_db(chunks)
    print(f"✅ New embeddings saved to ChromaDB at {vector_db_path}")

# Utility function to check existing data in ChromaDB (for debugging)
def debug_chromadb():
    """Debug function to check what's in ChromaDB"""
    try:
        client = chromadb.PersistentClient(path=vector_db_path)
        collection = client.get_collection(name="pdf_embeddings")
        
        # Get a sample of data
        sample_data = collection.get(limit=5, include=["metadatas", "documents"])
        
        print("🔍 ChromaDB Debug Information:")
        print(f"Total items in collection: {collection.count()}")
        print("\nSample entries:")
        
        for i, (metadata, doc) in enumerate(zip(sample_data["metadatas"], sample_data["documents"])):
            print(f"\nEntry {i+1}:")
            print(f"  Source: {os.path.basename(metadata.get('source', 'Unknown'))}")
            print(f"  Page: {metadata.get('page', 'Unknown')} (type: {type(metadata.get('page', 'Unknown'))})")
            print(f"  Content preview: {doc[:100]}...")
            
    except Exception as e:
        print(f"❌ Error debugging ChromaDB: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "debug":
        debug_chromadb()
    else:
        process_all_pdfs()