# Nutri-RAG Backend

Simple RAG (Retrieval-Augmented Generation) system for nutrition and health queries.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install and Run Ollama (for Llama 3)

```bash
# Install Ollama (if not already installed)
curl https://ollama.ai/install.sh | sh

# Pull Llama 3 model
ollama pull llama3

# Verify Ollama is running
ollama list
```

### 3. Populate Database

Place your PDF documents in `data/pdfs/` directory, then run:

```bash
python core/populate_database.py --reset
```

This will:
- Extract text from PDFs using PyMuPDF + PDFPlumber (working together)
- Chunk documents with RecursiveCharacterTextSplitter
- Generate embeddings with Sentence Transformers
- Store in ChromaDB

### 4. Test Query (CLI)

```bash
# General mode
python core/query_data.py "What are the health benefits of omega-3 fatty acids?"

# Clinical mode (asks for patient history)
python core/query_data.py "Dietary recommendations for diabetes" --mode clinical

# Custom top-k
python core/query_data.py "Symptoms of hypertension" --top-k 10
```

### 5. Start API Server

```bash
python api.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Query System

**POST** `/api/query`

Query the RAG system with a nutrition question.

```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Qué alimentos reducen la presión arterial?",
    "mode": "general",
    "top_k": 5
  }'
```

Request body:
```json
{
  "query": "Your question here",
  "mode": "general",      // "general" or "clinical"
  "top_k": 5              // Number of documents to retrieve
}
```
