import os
import json
import chromadb
from chromadb.utils import embedding_functions

CHUNKS_DIR = "/Users/sureshneupane/Documents/suresh/antigriavity/interview-preparetion/chatbot/laws/corporate-laws/chunks"
DB_DIR = "/Users/sureshneupane/Documents/suresh/antigriavity/interview-preparetion/chatbot/chroma_db"

def ingest_data():
    os.makedirs(DB_DIR, exist_ok=True)
    
    print("Connecting to ChromaDB...")
    # Initialize ChromaDB persistent client
    client = chromadb.PersistentClient(path=DB_DIR)
    
    print("Downloading/Loading Multilingual Embedding Model (This may take a minute on first run)...")
    # Set up Multilingual Embedding Function
    # This is critical for Nepali language semantic search.
    # The default Chroma model only understands English.
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    
    # Create or get collection
    collection = client.get_or_create_collection(
        name="nepal_corporate_laws",
        embedding_function=emb_fn
    )
    
    # Read all JSON chunk files
    json_files = [f for f in os.listdir(CHUNKS_DIR) if f.endswith('.json')]
    
    total_chunks = 0
    
    for filename in json_files:
        filepath = os.path.join(CHUNKS_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
            
        ids = []
        documents = []
        metadatas = []
        
        for chunk in chunks:
            ids.append(chunk["chunk_id"])
            documents.append(chunk["text"])
            
            # Ensure metadata values are compatible with ChromaDB
            meta = {}
            # Add filename to metadata so we know the source
            meta["source_file"] = filename.replace("_chunks.json", ".md")
            
            for k, v in chunk.get("metadata", {}).items():
                if isinstance(v, (str, int, float, bool)):
                    meta[k] = v
                else:
                    meta[k] = str(v)
                    
            metadatas.append(meta)
            
        # Add to ChromaDB in batches to avoid memory overload
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            collection.add(
                ids=ids[i:i+batch_size],
                documents=documents[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size]
            )
            
        print(f"✅ Ingested {len(chunks)} chunks from {filename}")
        total_chunks += len(chunks)
        
    print(f"\n🎉 Successfully ingested a total of {total_chunks} chunks into ChromaDB!")
    print(f"📁 Database saved at: {DB_DIR}")

if __name__ == "__main__":
    print("Starting ingestion into ChromaDB...\n" + "="*50)
    ingest_data()
