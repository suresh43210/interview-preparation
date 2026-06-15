import os
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()
pc_key = os.environ.get("PINECONE_API_KEY")
pc = Pinecone(api_key=pc_key)
index = pc.Index("nepal-corporate-laws")
embedder = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

def search(query):
    query_vector = embedder.encode(query).tolist()
    results = index.query(vector=query_vector, top_k=3, include_metadata=True)
    print(f"\nQuery: {query}")
    for match in results.matches:
        print(f"Score: {match.score:.4f} | Act: {match.metadata.get('Act Name')} | Sec: {match.metadata.get('Section')}")

search("bank kholna k garnu parchha")
search("बैंक खोल्न के गर्नुपर्छ")
