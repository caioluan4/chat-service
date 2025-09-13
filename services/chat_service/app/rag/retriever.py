
from langchain.vectorstores.base import VectorStoreRetriever
from langchain_community.vectorstores import Qdrant

from app.rag.vector_store import COLLECTION_NAME, get_embeddings, get_qdrant_client


def get_retriever() -> VectorStoreRetriever:
    """
    Inicializa e configura um retriever do Qdrant.

    O retriever é configurado para se conectar a uma coleção específica
    no Qdrant e utilizar um modelo de embeddings definido.

    Returns:
        Um objeto VectorStoreRetriever configurado para buscar os 3
        documentos (chunks) mais relevantes.
    """
    qdrant_client = Qdrant(
        client=get_qdrant_client(),
        collection_name=COLLECTION_NAME,
        embeddings=get_embeddings(),
    )

    # Configura o retriever para buscar os 3 chunks mais similares à consulta.
    retriever = qdrant_client.as_retriever(
        search_kwargs={"k": 3}
    )

    return retriever