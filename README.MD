# NourAI

An AI-powered nutrition assistant that provides personalized dietary recommendations using RAG (Retrieval-Augmented Generation) technology. Built with official nutritional guidelines from FAO, WHO, and PAHO.

## Features

### Core Capabilities

- **RAG-Powered Responses**: Retrieval-Augmented Generation grounded in official nutrition documents
- **Scientific Foundation**: All responses based on FAO, WHO, and PAHO (OPS) guidelines
- **7-Day Meal Plans**: Complete weekly diet plans with specific portions and macronutrient calculations
- **Allergy-Aware**: Automatically excludes foods based on user allergies
- **BMI Calculations**: Automatic BMI calculation with diet adjustments

### Clinical Data Support

- Age, gender, weight, and height tracking
- Medical conditions (diabetes, hypertension, etc.)
- Food allergies and intolerances
- Current medications
- Dietary preferences (vegetarian, vegan, etc.)
- Activity level (sedentary, light, moderate, intense)
- Data persisted locally in browser

### Chat System

- Persistent chat history with SQLite database
- Multiple conversation threads
- Create, load, and delete chats
- Message citations with source documents
- Copy messages to clipboard
- Feedback system (thumbs up/down)

### Multi-LLM Support

| Provider       | Type                   | Model                   |
| -------------- | ---------------------- | ----------------------- |
| **Ollama**     | Local, Free            | llama3.2:3b             |
| **Groq**       | Cloud, Free Tier       | llama-3.1-70b-versatile |
| **OpenRouter** | Cloud, Multiple Models | llama-3.1-70b-instruct  |

### Vector Database Options

| Provider     | Type  | Description                |
| ------------ | ----- | -------------------------- |
| **ChromaDB** | Local | Default, no setup required |
| **Pinecone** | Cloud | Scalable, serverless       |

### Document Processing

- PDF text and table extraction
- Recursive document chunking (500 chars, 200 overlap)
- Multilingual embeddings (intfloat/multilingual-e5-large)
- Document metadata from index file
- Similarity-based retrieval with configurable threshold

### Source Citations

- Document title and organization
- Publication year and author
- Direct links to source documents
- Similarity scores for transparency
- Collapsible citation details in UI

## Tech Stack

**Backend**

- Python + FastAPI
- LangChain for RAG orchestration
- Sentence Transformers for embeddings
- ChromaDB / Pinecone for vector storage
- SQLite for chat persistence

**Frontend**

- React 18 + TypeScript
- Vite
- Tailwind CSS + shadcn/ui
- Markdown rendering support

## Prerequisites

- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.ai) (if using local LLM)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/williamstevencole/NourAI.git NourAI
cd NourAI
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt

## Para re poblar la base de datos
python3 backend/core/populate_database.py --reset

python3 backend/api.py
```

## Terminal 2

```bash
cd frontend
npm i
npm run dev
```

## Terminal 3

```bash
ollama serve
```

## Terminal 4

```bash
ollama pull llama3.2:3b

ollama run llama3.2:3b
# Press Ctrl+D to exit interactive mode (model stays loaded)
```

### Step 2: Populate the Database

Place your PDF documents in `backend/data/pdfs/`, then run:

```bash
cd backend
python core/populate_database.py --reset
```

This will:

- Extract text and tables from PDFs
- Chunk documents with overlap
- Generate multilingual embeddings
- Store in your chosen vector database

### Step 3: Start the Backend

```bash
cd backend
python api.py
```

The API will be available at `http://localhost:8000`

### Step 4: Start the Frontend

```bash
cd frontend
npm run dev
```

The app will be available at `http://localhost:5173`

## API Endpoints

### Query System

**POST** `/api/query` - Query the RAG system

```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What foods help reduce blood pressure?",
    "top_k": 5,
    "clinical_data": {
      "age": 45,
      "gender": "male",
      "weight": 85,
      "height": 175,
      "conditions": ["hypertension"],
      "allergies": ["gluten"],
      "activity_level": "moderate"
    }
  }'
```

### Chat Management

| Method | Endpoint                   | Description       |
| ------ | -------------------------- | ----------------- |
| POST   | `/api/chats`               | Create new chat   |
| GET    | `/api/chats`               | List all chats    |
| GET    | `/api/chats/{id}`          | Get chat messages |
| POST   | `/api/chats/{id}/messages` | Save message      |
| DELETE | `/api/chats/{id}`          | Delete chat       |

### Health Check

**GET** `/api/health`

```bash
curl http://localhost:8000/api/health
```

## Testing & Evaluation

The project includes a RAGAS-based evaluation system to measure RAG performance.

### Setup

1. Get an OpenAI API key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Add it to your `backend/.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Run Evaluation

```bash
cd backend/test/scripts
python main.py
```

This evaluates the RAG system using 5 test cases and measures:

| Metric                 | Description                                 |
| ---------------------- | ------------------------------------------- |
| **Faithfulness**       | Does the response stay true to the context? |
| **Answer Relevancy**   | Is the response relevant to the question?   |
| **Context Recall**     | Were all necessary documents retrieved?     |
| **Context Precision**  | Are relevant docs ranked at the top?        |
| **Answer Correctness** | Is the response factually accurate?         |

Results are saved to `backend/test/scripts/evaluation_results/`.

## Project Structure

```
nourai/
├── backend/
│   ├── api.py                 # FastAPI server & endpoints
│   ├── config.py              # Configuration & providers
│   ├── core/
│   │   ├── populate_database.py  # PDF processing & indexing
│   │   ├── query_data.py         # RAG query logic
│   │   └── rag/                  # RAG components
│   ├── test/                  # RAGAS evaluation system
│   ├── utils/
│   │   ├── llm_factory.py        # Multi-LLM provider support
│   │   └── nutrition/            # Nutrition calculations
│   └── data/
│       ├── pdfs/              # Source PDF documents
│       ├── chroma/            # Local vector database
│       └── chats.db           # SQLite chat history
├── frontend/
│   └── src/
│       ├── components/        # React components
│       ├── services/          # API client
│       └── lib/               # Utilities
└── README.md
```

## Supported Health Conditions

The system provides specialized guidance for:

- Type 2 Diabetes
- Hypertension
- Obesity
- Cardiovascular diseases
- Pediatric nutrition
- Pregnancy nutrition

## License

MIT

---

Built with Python, React, and LangChain
