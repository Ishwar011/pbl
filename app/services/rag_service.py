import chromadb
from chromadb.utils import embedding_functions

# Initialize Chroma client
client = chromadb.Client()

embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    name="sar_regulations",
    embedding_function=embedding_function
)

def add_regulations():
    documents = [
        "Structuring involves multiple small transactions to avoid reporting thresholds.",
        "Rapid movement of funds to foreign jurisdictions may indicate layering in money laundering.",
        "High transaction volume inconsistent with customer risk profile may indicate suspicious activity."
    ]

    ids = ["reg1", "reg2", "reg3"]

    collection.add(documents=documents, ids=ids)


def retrieve_context(query: str):
    results = collection.query(
        query_texts=[query],
        n_results=2
    )

    return results["documents"][0]
