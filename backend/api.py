from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn

from core.query_data import query_rag
from config import TOP_K
from utils.chat_db import create_chat, save_message, get_chat_list, get_chat_messages, delete_chat

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
    chat_id: Optional[str] = None

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

class ChatCreateRequest(BaseModel):
    title: str

class ChatCreateResponse(BaseModel):
    chat_id: str

class ChatListResponse(BaseModel):
    chats: List[Dict[str, Any]]

class MessageSaveRequest(BaseModel):
    role: str
    content: str
    citations: Optional[List[Dict[str, Any]]] = None

class MessageSaveResponse(BaseModel):
    message_id: str

class ChatMessagesResponse(BaseModel):
    messages: List[Dict[str, Any]]


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "Nutri-RAG API",
        "version": "2.0.0",
        "endpoints": {
            "query": "POST /api/query",
            "create_chat": "POST /api/chats",
            "list_chats": "GET /api/chats",
            "get_chat": "GET /api/chats/{chat_id}",
            "save_message": "POST /api/chats/{chat_id}/messages",
            "delete_chat": "DELETE /api/chats/{chat_id}",
            "health": "GET /api/health"
        }
    }


@app.post("/api/query", response_model=QueryResponse)
def query(request: QueryRequest):
    """
    Query the RAG system and optionally save to chat history.
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

        # Save messages to chat if chat_id is provided
        if request.chat_id:
            try:
                # Save user message
                user_msg_id = save_message(request.chat_id, "user", request.query)
                print(f"Successfully saved user message with ID: {user_msg_id}")

                # Save assistant message with sources as citations
                try:
                    citations = [{
                        "id": f"cite-{i}",
                        "label": f"[{i + 1}]",
                        "organization": source.organization,
                        "year": source.year,
                        "title": source.title,
                        "url": source.link,
                        "excerpt": f"Similitud: {source.similarity}"
                    } for i, source in enumerate(result["sources"])]

                    assistant_msg_id = save_message(request.chat_id, "assistant", result["answer"], citations, result["sources"])
                except Exception as cite_error:
                    print(f"Error creating citations: {cite_error}")
                    # Save without citations if citations fail, but with sources
                    assistant_msg_id = save_message(request.chat_id, "assistant", result["answer"], sources=result["sources"])
                print(f"Successfully saved assistant message with ID: {assistant_msg_id}")
            except Exception as save_error:
                # Log but don't fail the query if saving fails
                print(f"Error: Failed to save chat message: {save_error}")
                import traceback
                traceback.print_exc()

        return QueryResponse(
            query=request.query,
            answer=result["answer"],
            sources=[Source(**s) for s in result["sources"]] # Convert source dicts to Source models
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Chat management endpoints
@app.post("/api/chats", response_model=ChatCreateResponse)
def create_new_chat(request: ChatCreateRequest):
    """Create a new chat thread."""
    try:
        chat_id = create_chat(request.title)
        return ChatCreateResponse(chat_id=chat_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create chat: {str(e)}")


@app.get("/api/chats", response_model=ChatListResponse)
def list_chats(limit: int = 50):
    """Get list of chats."""
    try:
        chats = get_chat_list(limit)
        return ChatListResponse(chats=chats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list chats: {str(e)}")


@app.get("/api/chats/{chat_id}", response_model=ChatMessagesResponse)
def get_chat(chat_id: str):
    """Get all messages for a specific chat."""
    try:
        messages = get_chat_messages(chat_id)
        if not messages:
            raise HTTPException(status_code=404, detail="Chat not found")
        return ChatMessagesResponse(messages=messages)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chat: {str(e)}")


@app.post("/api/chats/{chat_id}/messages", response_model=MessageSaveResponse)
def save_chat_message(chat_id: str, request: MessageSaveRequest):
    """Save a message to a chat."""
    try:
        message_id = save_message(chat_id, request.role, request.content, request.citations)
        return MessageSaveResponse(message_id=message_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save message: {str(e)}")


@app.delete("/api/chats/{chat_id}")
def delete_chat_endpoint(chat_id: str):
    """Delete a chat and all its messages."""
    try:
        success = delete_chat(chat_id)
        if not success:
            raise HTTPException(status_code=404, detail="Chat not found")
        return {"message": "Chat deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete chat: {str(e)}")


@app.get("/api/health")
def health():
    """Health check"""
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
