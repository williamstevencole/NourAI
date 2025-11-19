from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from core.query_data import query_rag
from config import TOP_K

app = FastAPI(
    title="Nutri-RAG API",
    description="RAG system for nutrition and health queries",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ClinicalData(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    conditions: Optional[list[str]] = None
    allergies: Optional[list[str]] = None
    medications: Optional[list[str]] = None
    diet_type: Optional[str] = None
    activity_level: Optional[str] = None

class QueryRequest(BaseModel):
    query: str
    top_k: int = TOP_K
    clinical_data: Optional[ClinicalData] = None

class Source(BaseModel):
    title: str
    organization: str
    organization_acronym: Optional[str] = ""
    year: Optional[int] = None
    author: str
    link: Optional[str] = None
    similarity: str

class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: list[Source]


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "Nutri-RAG API",
        "version": "2.0.0",
        "endpoints": {
            "query": "POST /api/query",
            "health": "GET /api/health"
        }
    }


@app.post("/api/query", response_model=QueryResponse)
def query(request: QueryRequest):
    """
    Query the RAG system.
    """
    try:
        clinical_dict = None
        if request.clinical_data:
            clinical_dict = request.clinical_data.model_dump(exclude_none=True) # Convert to dict excluding None values

        result = query_rag(
            query_text=request.query,
            top_k=request.top_k,
            clinical_data=clinical_dict
        )

        return QueryResponse(
            query=request.query,
            answer=result["answer"],
            sources=[Source(**s) for s in result["sources"]] # Convert source dicts to Source models
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
def health():
    """Health check"""
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
