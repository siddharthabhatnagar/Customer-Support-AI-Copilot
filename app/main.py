"""Customer Support AI Copilot - FastAPI Application."""
import os
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.config import settings
from app.models.schemas import (
    Ticket,
    TicketCreateRequest,
    TriageResult,
    RAGResponse,
    KnowledgeArticle,
    KnowledgeArticleCreate,
    AnalyticsSummary,
    SettingsUpdateRequest,
    ConnectionTestRequest,
    ConnectionTestResponse,
)
from app.services.ticket_service import ticket_service
from app.services.rag_service import rag_service
from app.services.ai_service import ai_service
from app.services.analytics_service import analytics_service

app = FastAPI(
    title="Customer Support AI Copilot",
    description="Business-oriented AI ticket classification, RAG responses, structured summaries, sentiment detection, and escalation recommendations.",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

# Mount static directory
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/", include_in_schema=False)
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse({"status": "Customer Support AI Copilot API Running"})

# =============================================================================
# SYSTEM HEALTH & SETTINGS ENDPOINTS
# =============================================================================

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "groq_configured": bool(settings.groq_api_key),
        "groq_model": settings.groq_model,
        "nvidia_configured": bool(settings.nvidia_api_key),
        "nvidia_model": settings.nvidia_embedding_model,
        "using_nvidia_embeddings": rag_service.is_using_nvidia,
        "total_tickets": len(ticket_service.tickets),
        "total_articles": len(rag_service.articles)
    }

@app.post("/api/settings")
async def update_settings(req: SettingsUpdateRequest):
    settings.update_keys(
        groq_key=req.groq_api_key,
        nvidia_key=req.nvidia_api_key,
        groq_model=req.groq_model,
        nvidia_model=req.nvidia_embedding_model
    )
    # Reindex vector retriever with new NVIDIA key if updated
    rag_service.reindex()
    return {
        "message": "Settings updated successfully",
        "groq_configured": bool(settings.groq_api_key),
        "groq_model": settings.groq_model,
        "nvidia_configured": bool(settings.nvidia_api_key),
        "nvidia_model": settings.nvidia_embedding_model,
        "using_nvidia_embeddings": rag_service.is_using_nvidia
    }

@app.post("/api/settings/test", response_model=ConnectionTestResponse)
async def test_connections(req: ConnectionTestRequest):
    groq_res = ai_service.test_groq_connection(req.groq_api_key)
    nvidia_res = rag_service.test_nvidia_connection(req.nvidia_api_key)

    return ConnectionTestResponse(
        groq_connected=groq_res["connected"],
        groq_latency_ms=groq_res.get("latency_ms"),
        groq_model=groq_res.get("model"),
        groq_message=groq_res["message"],
        nvidia_connected=nvidia_res["connected"],
        nvidia_latency_ms=nvidia_res.get("latency_ms"),
        nvidia_model=nvidia_res.get("model"),
        nvidia_message=nvidia_res["message"],
    )

# =============================================================================
# TICKET MANAGEMENT ENDPOINTS
# =============================================================================

@app.get("/api/tickets", response_model=List[Ticket])
async def list_tickets(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    return ticket_service.list_tickets(status=status, priority=priority, category=category, search=search)

@app.get("/api/tickets/{ticket_id}", response_model=Ticket)
async def get_ticket(ticket_id: str):
    ticket = ticket_service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@app.post("/api/tickets", response_model=Ticket)
async def create_ticket(req: TicketCreateRequest):
    ticket = ticket_service.create_ticket(req)
    # Automatically triage newly created ticket so user gets instant copilot analysis!
    ticket_service.triage_ticket(ticket.id)
    return ticket_service.get_ticket(ticket.id)

@app.post("/api/tickets/{ticket_id}/triage", response_model=TriageResult)
async def triage_ticket(ticket_id: str):
    result = ticket_service.triage_ticket(ticket_id)
    if not result:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return result

@app.post("/api/tickets/triage-all")
async def triage_all_tickets():
    return ticket_service.triage_all()

@app.post("/api/tickets/{ticket_id}/resolve", response_model=Ticket)
async def resolve_ticket(ticket_id: str):
    ticket = ticket_service.resolve_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@app.post("/api/tickets/{ticket_id}/draft-reply", response_model=RAGResponse)
async def generate_draft_reply(
    ticket_id: str,
    tone: str = Body(..., embed=True)
):
    ticket = ticket_service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    citations = rag_service.search(f"{ticket.subject} {ticket.body}", top_k=3)
    draft = ai_service.generate_rag_response(ticket.subject, ticket.body, citations, tone=tone)
    ticket.resolution_draft = draft
    return draft

# =============================================================================
# KNOWLEDGE BASE & RAG ENDPOINTS
# =============================================================================

@app.get("/api/knowledge-base", response_model=List[KnowledgeArticle])
async def list_knowledge_base():
    return rag_service.get_all_articles()

@app.post("/api/knowledge-base", response_model=KnowledgeArticle)
async def add_knowledge_article(req: KnowledgeArticleCreate):
    article_dict = {
        "title": req.title,
        "category": req.category,
        "content": req.content,
        "tags": req.tags,
        "last_updated": "2026-10-21"
    }
    return rag_service.add_article(article_dict)

@app.get("/api/knowledge-base/search")
async def search_knowledge_base(q: str = Query(...), top_k: int = Query(3)):
    citations = rag_service.search(query=q, top_k=top_k)
    return {"query": q, "results": [c.dict() for c in citations]}

# =============================================================================
# ANALYTICS & ROI METRICS
# =============================================================================

@app.get("/api/analytics", response_model=AnalyticsSummary)
async def get_analytics():
    return analytics_service.get_summary()
