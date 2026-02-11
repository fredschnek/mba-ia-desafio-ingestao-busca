import os

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# Validate common env vars
for item in ('MODEL', 'DATABASE_URL', 'PG_VECTOR_COLLECTION_NAME', 'PDF_PATH'):
    if not os.getenv(item):
        raise RuntimeError(f'Environment variable {item} is not set')

MODEL = os.getenv('MODEL')

# Validate only the env vars needed for the selected model
if MODEL == 'openai':
    if not os.getenv('OPENAI_EMBEDDING_MODEL'):
        raise RuntimeError('Environment variable OPENAI_EMBEDDING_MODEL is not set')
else:
    if not os.getenv('GOOGLE_EMBEDDING_MODEL'):
        raise RuntimeError('Environment variable GOOGLE_EMBEDDING_MODEL is not set')

GOOGLE_EMBEDDING_MODEL = os.getenv('GOOGLE_EMBEDDING_MODEL')
OPENAI_EMBEDDING_MODEL = os.getenv('OPENAI_EMBEDDING_MODEL')
DATABASE_URL = os.getenv('DATABASE_URL')
PG_VECTOR_COLLECTION_NAME = os.getenv('PG_VECTOR_COLLECTION_NAME')
PDF_PATH = os.getenv('PDF_PATH')


def ingest_pdf():
    print('Carregando PDF...')
    documents = _load_pdf()

    print('Processando PDF...')
    chunks = _split_in_chunks(documents)
    enriched_documents = _enrich(chunks)

    ids = [f'DOC-{i}' for i in range(len(enriched_documents))]

    if MODEL == 'openai':
        embeddings = OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL)
    else:
        embeddings = GoogleGenerativeAIEmbeddings(model=GOOGLE_EMBEDDING_MODEL)

    print('Conectando ao DB...')
    store = PGVector(
        embeddings=embeddings,
        collection_name=PG_VECTOR_COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
    )

    print('Salvando no DB...')
    store.add_documents(documents=enriched_documents, ids=ids)

    print('Ingestão finalizada!')


def _load_pdf():
    loader = PyPDFLoader(PDF_PATH)
    return loader.load()


def _split_in_chunks(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(documents)

    if not chunks:
        raise SystemExit(1)

    return chunks


def _enrich(chunks):
    return [
        Document(
            page_content=document.page_content,
            metadata={k: v for k, v in document.metadata.items() if v not in ('', None)},
        )
        for document in chunks
    ]


if __name__ == '__main__':
    ingest_pdf()
