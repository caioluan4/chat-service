from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_and_split_pdf(file_path: str):
    """
    Carrega um arquivo PDF a partir do seu caminho e o divide em pedaços (chunks)
    menores para facilitar o processamento e a busca.
    """
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # Estratégia para dividir o texto em pedaços de 1000 caracteres
    # com uma sobreposição de 150 caracteres entre eles.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    chunks = text_splitter.split_documents(documents)
    return chunks