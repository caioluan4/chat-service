import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant

from qdrant_client import QdrantClient 

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "documentos"

def get_embeddings():
    """
    Cria e retorna um modelo embedding da HuggingFace.
    Este modelo transforma o texto em vetores numéricos.
    """
   
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_qdrant_client():
    """
    Retorna um cliente para interagir diretamente com a API do Qdrant.
    """
    return QdrantClient(url=QDRANT_URL)

def save_chunks_to_qdrant(chunks):
    """
    Salva os "pedaços" (chunks) de texto no banco de dados vetorial Qdrant.
    """
    Qdrant.from_documents(
        documents=chunks,
        embeddings=get_embeddings(),
        url=QDRANT_URL,
        collection_name=COLLECTION_NAME,
    )
    print(f"Salvou {len(chunks)} chunks na coleção '{COLLECTION_NAME}'.")
    