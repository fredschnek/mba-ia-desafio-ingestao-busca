import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

# Validate common env vars
for item in ('MODEL', 'DATABASE_URL', 'PG_VECTOR_COLLECTION_NAME'):
    if not os.getenv(item):
        raise RuntimeError(f'Environment variable {item} is not set')

MODEL = os.getenv('MODEL')

# Validate only the env vars needed for the selected model
if MODEL == 'openai':
    for item in ('OPENAI_EMBEDDING_MODEL', 'OPENAI_LLM_MODEL'):
        if not os.getenv(item):
            raise RuntimeError(f'Environment variable {item} is not set')
else:
    for item in ('GOOGLE_EMBEDDING_MODEL', 'GOOGLE_LLM_MODEL'):
        if not os.getenv(item):
            raise RuntimeError(f'Environment variable {item} is not set')

GOOGLE_EMBEDDING_MODEL = os.getenv('GOOGLE_EMBEDDING_MODEL')
GOOGLE_LLM_MODEL = os.getenv('GOOGLE_LLM_MODEL')
OPENAI_EMBEDDING_MODEL = os.getenv('OPENAI_EMBEDDING_MODEL')
OPENAI_LLM_MODEL = os.getenv('OPENAI_LLM_MODEL')
DATABASE_URL = os.getenv('DATABASE_URL')
PG_VECTOR_COLLECTION_NAME = os.getenv('PG_VECTOR_COLLECTION_NAME')

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""


def search_prompt(question):
    if not question:
        raise ValueError('A question is required')

    # Build the LLM chain with the prompt template
    llm_model = OPENAI_LLM_MODEL if MODEL == 'openai' else GOOGLE_LLM_MODEL
    chat_model = init_chat_model(model=llm_model, model_provider=MODEL, temperature=0.1)

    template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    chain = template | chat_model

    # Instantiate only the needed embedding
    if MODEL == 'openai':
        embeddings = OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL)
    else:
        embeddings = GoogleGenerativeAIEmbeddings(model=GOOGLE_EMBEDDING_MODEL)

    # Search the DB for the 10 most similar vectors
    store = PGVector(
        embeddings=embeddings,
        collection_name=PG_VECTOR_COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
    )
    result = store.similarity_search(question, k=10)
    context = '\n'.join(document.page_content for document in result)

    # Invoke the chain with context and user question
    response = chain.invoke({
        'contexto': context,
        'pergunta': question,
    })

    return response
