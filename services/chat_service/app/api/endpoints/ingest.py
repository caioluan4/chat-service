import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.rag.loader import load_and_split_pdf
from app.core.rag.vector_store import save_chunks_to_qdrant

router = APIRouter()

# O caminho para a pasta /documents de dentro do contêiner.
# Mapeado no docker-compose.yml para a pasta ./documents do seu projeto.
DOCUMENTS_DIR = "/app/documents"

@router.post("/ingest", status_code=201, summary="Processa e armazena um documento PDF")
async def ingest_document(file: UploadFile = File(...)):
    """
    Recebe um upload de arquivo PDF, processa-o e armazena seus vetores no Qdrant.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Somente arquivos PDF são aceitos.")

    # Garante que a pasta /app/documents exista dentro do contêiner
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)

    file_path = os.path.join(DOCUMENTS_DIR, file.filename)

    try:
        # Salva o arquivo PDF no volume compartilhado
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 1. Carrega o PDF e o divide em pedaços
        chunks = load_and_split_pdf(file_path)
        if not chunks:
            raise HTTPException(status_code=500, detail="Não foi possível extrair conteúdo do PDF.")

        # 2. Transforma os pedaços em vetores e salva no Qdrant
        save_chunks_to_qdrant(chunks)

        return {"message": f"Documento '{file.filename}' processado com sucesso."}

    finally:
        # Apaga o arquivo PDF temporário após o processamento
        if os.path.exists(file_path):
            os.remove(file_path)