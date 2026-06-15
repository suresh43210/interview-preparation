import os
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index("nepal-corporate-laws")
embedder = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

queries = [
    "श्रम ऐन अनुसार महिला सुत्केरी बिदा कति दिन पाइन्छ?",
    "How many days of maternity leave does a woman get according to the Labor Act?"
]

for q in queries:
    print(f"\n--- Query: {q} ---")
    vec = embedder.encode(q).tolist()
    res = index.query(vector=vec, top_k=3, include_metadata=True)
    for m in res.matches:
        print(f"Score: {m.score:.4f} | Act: {m.metadata.get('Act Name')} | Sec: {m.metadata.get('Section')}")
        print(f"Text snippet: {m.metadata.get('text')[:100]}...")
