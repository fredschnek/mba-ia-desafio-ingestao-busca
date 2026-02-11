# Desafio MBA Engenharia de Software com IA - Full Cycle

Sistema de **Ingestão e Busca Semântica** com LangChain e PostgreSQL (pgVector).
O software lê um arquivo PDF, armazena seus dados vetorizados no banco e permite que o usuário faça perguntas via CLI, recebendo respostas baseadas exclusivamente no conteúdo do documento.

---

## Pré-requisitos

- **Python 3.10+**
- **Docker** e **Docker Compose**
- Chave de API da **Google (Gemini)** e/ou **OpenAI**

---

## Configuração do Ambiente

### 1. Clonar o repositório

```bash
git clone https://github.com/fredschnek/mba-ia-desafio-ingestao-busca.git
cd mba-ia-desafio-ingestao-busca
```

### 2. Criar e ativar o ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar as variáveis de ambiente

Duplique o arquivo `.env.example` e renomeie para `.env`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e preencha as variáveis necessárias:

| Variavel | Descricao |
|----------|-----------|
| `GOOGLE_API_KEY` | Sua chave de API do Google Gemini |
| `OPENAI_API_KEY` | Sua chave de API da OpenAI |
| `MODEL` | Provedor a ser usado: `openai` (padrao) ou `google_genai` |
| `DATABASE_URL` | URL de conexao com o PostgreSQL (ja preenchida com o padrao do Docker Compose) |
| `PG_VECTOR_COLLECTION_NAME` | Nome da colecao de vetores (padrao: `pdf_collection`) |
| `PDF_PATH` | Caminho para o arquivo PDF (padrao: `./document.pdf`) |

> **Nota:** Voce so precisa preencher a chave de API do provedor selecionado em `MODEL`. Se usar `google_genai`, basta a `GOOGLE_API_KEY`. Se usar `openai`, basta a `OPENAI_API_KEY`.

---

## Obtendo as Chaves de API

### Google Gemini

1. Acesse o [Google AI Studio](https://aistudio.google.com/api-keys)
2. Faca login com sua conta Google
3. Clique em **"Create API Key"**
4. Copie a chave gerada e cole na variável `GOOGLE_API_KEY` do arquivo `.env`

Documentação oficial: [Como usar chaves da API Gemini](https://ai.google.dev/gemini-api/docs/api-key?hl=pt-BR)

### OpenAI

1. Acesse [OpenAI API Keys](https://platform.openai.com/account/api-keys)
2. Faça login ou crie uma conta
3. Clique em **"Create new secret key"**
4. Copie a chave gerada e cole na variável `OPENAI_API_KEY` do arquivo `.env`

> **Importante:** Nunca compartilhe suas chaves de API publicamente.

---

## Ordem de Execução

### 1. Subir o banco de dados

```bash
docker compose up -d
```

Isso inicia o PostgreSQL com a extensão pgVector. Aguarde alguns segundos para o banco ficar pronto.

### 2. Executar a ingestao do PDF

```bash
python src/ingest.py
```

Este script:
- Lê o arquivo PDF configurado em `PDF_PATH`
- Divide o conteúdo em chunks de 1000 caracteres com overlap de 150
- Gera embeddings usando o modelo configurado (Google ou OpenAI)
- Armazena os vetores no PostgreSQL

### 3. Rodar o chat

```bash
python src/chat.py
```

O chat interativo permite fazer perguntas sobre o conteúdo do PDF:

```
Faça sua pergunta:
Qual o faturamento da Empresa SuperTechIABrazil?

PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento foi de 10 milhões de reais.

Caso queira sair, digite "exit".
```

Perguntas fora do contexto do documento receberão a resposta:
> "Nao tenho informacoes necessarias para responder sua pergunta."

---

## Estrutura do Projeto

```
├── docker-compose.yml        # Servicos Docker (PostgreSQL + pgVector)
├── requirements.txt          # Dependencias Python
├── .env.example              # Template de variaveis de ambiente
├── src/
│   ├── ingest.py             # Script de ingestao do PDF
│   ├── search.py             # Logica de busca semantica e chamada a LLM
│   └── chat.py               # Interface CLI para interacao com o usuario
├── document.pdf              # PDF para ingestao
└── README.md                 # Este arquivo
```

---

## Tecnologias Utilizadas

- **Python** - Linguagem principal
- **LangChain** - Framework para orquestração de LLMs e RAG
- **PostgreSQL + pgVector** - Banco de dados vetorial
- **Docker Compose** - Gerenciamento de containers
- **OpenAI / Google Gemini** - Modelos de embeddings e LLM
