import os
import math
import google.generativeai as genai

documents = [
    "Structuring involves multiple small transactions to avoid reporting thresholds.",
    "Rapid movement of funds to foreign jurisdictions may indicate layering in money laundering.",
    "High transaction volume inconsistent with customer risk profile may indicate suspicious activity."
]

# We will cache the embeddings in memory
doc_embeddings = []

def get_embedding(text):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return [0.0] * 768 # Dummy fallback if no key
    
    genai.configure(api_key=api_key)
    result = genai.embed_content(
        model="models/embedding-001",
        content=text,
        task_type="retrieval_document",
    )
    return result['embedding']

def cosine_similarity(v1, v2):
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude1 = math.sqrt(sum(a * a for a in v1))
    magnitude2 = math.sqrt(sum(b * b for b in v2))
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    return dot_product / (magnitude1 * magnitude2)

def add_regulations():
    global doc_embeddings
    # Clear existing to prevent duplicates on multiple calls
    doc_embeddings.clear()
    for doc in documents:
        doc_embeddings.append(get_embedding(doc))

def retrieve_context(query: str):
    if not doc_embeddings:
        add_regulations()
        
    query_embedding = get_embedding(query)
    
    # Calculate similarities
    similarities = []
    for i, doc_emb in enumerate(doc_embeddings):
        sim = cosine_similarity(query_embedding, doc_emb)
        similarities.append((sim, documents[i]))
    
    # Sort by similarity in descending order
    similarities.sort(key=lambda x: x[0], reverse=True)
    
    # Return top 2 matching documents
    return [similarities[0][1], similarities[1][1]]
