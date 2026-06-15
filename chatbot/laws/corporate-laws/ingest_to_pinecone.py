import os
import json
import time
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")

CHUNKS_DIR = "chatbot/laws/corporate-laws/chunks"
INDEX_NAME = "nepal-corporate-laws"
DIMENSION = 384  # dimension size for paraphrase-multilingual-MiniLM-L12-v2

def ingest_to_pinecone():
    if not PINECONE_API_KEY:
        print("❌ Error: PINECONE_API_KEY not found in .env")
        return

    print("🔌 Connecting to Pinecone...")
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Check if index exists, create if not
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
    if INDEX_NAME not in existing_indexes:
        print(f"🏗️ Creating new index '{INDEX_NAME}' (dimension={DIMENSION})...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        # Wait for index to be ready
        while not pc.describe_index(INDEX_NAME).status['ready']:
            time.sleep(1)

    print(f"✅ Connected to index '{INDEX_NAME}'")
    index = pc.Index(INDEX_NAME)

    print("⏳ Loading Multilingual Embedding Model (paraphrase-multilingual-MiniLM-L12-v2)...")
    # This model natively understands Nepali!
    model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

    # Read all JSON chunk files
    json_files = [f for f in os.listdir(CHUNKS_DIR) if f.endswith('.json')]
    
    total_chunks = 0
    
    for filename in json_files:
        filepath = os.path.join(CHUNKS_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
            
        vectors = []
        
        print(f"⚙️ Processing {len(chunks)} chunks from {filename}...")
        for chunk in chunks:
            text = chunk["text"]
            # Generate embedding vector
            embedding = model.encode(text).tolist()
            
            # Prepare metadata
            meta = {
                "text": text,  # Crucial: store the actual text so we can retrieve it!
                "source_file": filename.replace("_chunks.json", ".md")
            }
            
            # Add existing metadata (Act Name, Part, Section, etc.)
            for k, v in chunk.get("metadata", {}).items():
                if isinstance(v, (str, int, float, bool, list)):
                    meta[k] = v
                else:
                    meta[k] = str(v)
            
            vectors.append({
                "id": chunk["chunk_id"],
                "values": embedding,
                "metadata": meta
            })
            
        # Upsert to Pinecone in batches of 100
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i+batch_size]
            index.upsert(vectors=batch)
            
        print(f"✅ Upserted {len(chunks)} chunks from {filename}")
        total_chunks += len(chunks)
        
    print(f"\n🎉 Successfully ingested a total of {total_chunks} chunks into Pinecone Cloud!")

if __name__ == "__main__":
    print("Starting Pinecone ingestion pipeline...\n" + "="*50)
    ingest_to_pinecone()
