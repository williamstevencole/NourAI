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

Response:
```json
{
  "query": "¿Qué alimentos reducen la presión arterial?",
  "answer": "Los alimentos ricos en potasio...",
  "sources": [
    {
      "filename": "hipertension-arterial-gpc.pdf",
      "source": "/path/to/file",
      "chunk_index": 42
    }
  ]
}
```

### Health Check

**GET** `/api/health`

```bash
curl "http://localhost:8000/api/health"
```

Response:
```json
{
  "status": "ok"
}
```

### Interactive Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Architecture

### Ingestion Pipeline
```
PDFs → [PyMuPDF + PDFPlumber] → Chunks → [Sentence Transformers] → ChromaDB
```

### Query Pipeline
```
Query → [Sentence Transformers] → ChromaDB → Context → [LangChain + Llama 3] → Answer
```

## Project Structure

```
backend/
├── config.py                    # Configuration & system prompts
├── api.py                       # FastAPI server
│
├── core/                        # Core RAG functionality
│   ├── populate_database.py    # Ingest PDFs into ChromaDB
│   └── query_data.py           # Query RAG system (CLI)
│
├── utils/                       # Utility functions
│   ├── pdf_utils.py            # PyMuPDF + PDFPlumber loader
│   └── embedding_function.py   # Sentence Transformers wrapper
│
├── data/                        # Data storage
│   ├── pdfs/                   # Input PDF documents
│   └── chroma/                 # ChromaDB vector store
│
├── requirements.txt
└── README.md
```

## Configuration

Edit `config.py` to customize:

```python
# Models
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "llama3"

# Chunking
CHUNK_SIZE = 800
CHUNK_OVERLAP = 80

# Retrieval
TOP_K = 5

# System Prompts
SYSTEM_PROMPT_GENERAL = "..."      # For general queries
SYSTEM_PROMPT_CLINICAL = "..."     # For clinical context (asks patient history)
```

## Key Features

✅ **Dual PDF extraction**: PyMuPDF (fast) + PDFPlumber (tables, OCR) working together
✅ **Local embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
✅ **Llama 3**: Via Ollama
✅ **Auto language detection**: Responds in same language as query
✅ **Clean responses**: No source citations in answer text, only in JSON metadata
✅ **Two modes**:
  - **General**: Direct answers to nutrition questions
  - **Clinical**: Asks for patient history before responding

## Example Usage

### Python Client

```python
import requests

response = requests.post(
    "http://localhost:8000/api/query",
    json={
        "query": "What vitamins are essential for bone health?",
        "mode": "general",
        "top_k": 5
    }
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Sources: {len(result['sources'])}")
```

### JavaScript/Fetch

```javascript
const response = await fetch('http://localhost:8000/api/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: '¿Beneficios de la dieta mediterránea?',
    mode: 'general',
    top_k: 5
  })
});

const data = await response.json();
console.log(data.answer);
```

## Troubleshooting

### Empty database (returns "No encontré información relevante")
```bash
# Check document count
python -c "
from langchain_community.vectorstores import Chroma
from utils.embedding_function import get_embedding_function
from config import CHROMA_PATH
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embedding_function())
print(f'Documents: {db._collection.count()}')
"

# If 0, populate database
python core/populate_database.py --reset
```

### Ollama not running
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve
```

### Model not found
```bash
# Pull Llama 3
ollama pull llama3

# Verify
ollama list
```

### ChromaDB telemetry errors
Already disabled in `config.py`:
```python
os.environ["ANONYMIZED_TELEMETRY"] = "False"
```

## Performance

- **PDF Loading**: ~1-5 seconds per document
- **Embedding**: ~100 chunks/second (CPU)
- **Retrieval**: <100ms
- **LLM Generation**: 2-10 seconds (CPU), faster with GPU
- **Total Query Time**: ~3-15 seconds

## Hardware Requirements

**Minimum**:
- 8GB RAM
- CPU only (slower)

**Recommended**:
- 16GB+ RAM
- NVIDIA GPU (optional, for faster inference)
- SSD storage

## Tech Stack

- **PDF Processing**: PyMuPDF + PDFPlumber
- **Embeddings**: Sentence Transformers
- **Vector DB**: ChromaDB
- **LLM**: Llama 3 (via Ollama)
- **Framework**: LangChain
- **API**: FastAPI
