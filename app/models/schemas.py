from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ClassificationResult(BaseModel):
    category: str = Field(..., description="High-level category e.g. Billing, Technical, Security")
    subcategory: str = Field(..., description="Specific sub-area e.g. Webhook Timeout, Refund")
    priority: str = Field(..., description="Urgent, High, Medium, Low")
    urgency_score: int = Field(default=50, ge=0, le=100, description="0-100 urgency score")
    suggested_tags: List[str] = Field(default_factory=list)
    sla_target: str = Field(default="4 hours", description="Target SLA resolution or response window")

class SentimentResult(BaseModel):
    sentiment: str = Field(..., description="Frustrated, Angry, Neutral, Satisfied, Delighted")
    score: int = Field(default=50, ge=0, le=100, description="Customer satisfaction/happiness score 0-100")
    churn_risk: str = Field(default="Low", description="Low, Moderate, High, Severe")
    emotional_drivers: List[str] = Field(default_factory=list, description="Key triggering phrases or concerns")
    tone_detected: str = Field(default="Professional/Direct", description="Detected customer tone")

class StructuredSummary(BaseModel):
    customer_goal: str = Field(..., description="What the customer is trying to accomplish")
    observed_symptoms: List[str] = Field(default_factory=list, description="Errors, symptoms, broken behaviors")
    customer_attempts: str = Field(default="", description="Actions customer already took")
    root_cause_hypothesis: str = Field(default="", description="Probable underlying cause")
    action_items: List[str] = Field(default_factory=list, description="Next concrete operational steps")

class EscalationRecommendation(BaseModel):
    escalate: bool = Field(..., description="Whether ticket requires human escalation")
    target_tier: str = Field(..., description="Tier 1 Support, Tier 2 Engineering, Billing Ops, Security, etc.")
    target_department: str = Field(..., description="Department assigned")
    justification: str = Field(..., description="Clear rationale based on SLA, technical depth, or financial impact")
    pre_escalation_checklist: List[str] = Field(default_factory=list, description="Checklist items before handover")

class Citation(BaseModel):
    doc_id: str
    title: str
    relevance_score: float
    snippet: str

class RAGResponse(BaseModel):
    draft_reply: str = Field(..., description="AI suggested customer-ready reply")
    citations: List[Citation] = Field(default_factory=list, description="Knowledge base sources used")
    confidence: float = Field(default=0.92, description="Confidence score 0.0 to 1.0")
    suggested_actions: List[str] = Field(default_factory=list, description="Recommended next actions for agent")

class TriageResult(BaseModel):
    ticket_id: str
    classification: ClassificationResult
    sentiment: SentimentResult
    summary: StructuredSummary
    escalation: EscalationRecommendation
    rag_draft: Optional[RAGResponse] = None
    processed_at: str

class Ticket(BaseModel):
    id: str
    customer_name: str
    customer_email: str
    company: str
    customer_tier: str = "Standard" # Free, Standard, Pro, Enterprise
    subject: str
    body: str
    created_at: str
    status: str = "Open" # Open, In Progress, Resolved, Escalated
    priority: str = "Medium"
    category: Optional[str] = None
    subcategory: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    sentiment: Optional[str] = None
    sentiment_score: Optional[int] = None
    churn_risk: Optional[str] = None
    summary: Optional[StructuredSummary] = None
    escalation: Optional[EscalationRecommendation] = None
    resolution_draft: Optional[RAGResponse] = None
    is_triaged: bool = False
    assigned_agent: Optional[str] = None

class TicketCreateRequest(BaseModel):
    customer_name: str
    customer_email: str
    company: Optional[str] = "Acme Corp"
    customer_tier: Optional[str] = "Standard"
    subject: str
    body: str
    priority: Optional[str] = "Medium"

class KnowledgeArticle(BaseModel):
    id: str
    title: str
    category: str
    content: str
    tags: List[str] = Field(default_factory=list)
    last_updated: str

class KnowledgeArticleCreate(BaseModel):
    title: str
    category: str
    content: str
    tags: List[str] = Field(default_factory=list)

class AnalyticsSummary(BaseModel):
    total_tickets: int
    open_tickets: int
    triaged_tickets: int
    escalated_tickets: int
    resolved_tickets: int
    estimated_hours_saved: float
    deflection_rate_pct: float
    avg_first_response_time_min: float
    manual_response_baseline_hr: float
    category_distribution: Dict[str, int]
    sentiment_distribution: Dict[str, int]
    priority_distribution: Dict[str, int]
    escalation_rate_pct: float

class SettingsUpdateRequest(BaseModel):
    groq_api_key: Optional[str] = None
    nvidia_api_key: Optional[str] = None
    groq_model: Optional[str] = None
    nvidia_embedding_model: Optional[str] = None

class ConnectionTestRequest(BaseModel):
    groq_api_key: Optional[str] = None
    nvidia_api_key: Optional[str] = None

class ConnectionTestResponse(BaseModel):
    groq_connected: bool
    groq_latency_ms: Optional[int] = None
    groq_model: Optional[str] = None
    groq_message: str
    nvidia_connected: bool
    nvidia_latency_ms: Optional[int] = None
    nvidia_model: Optional[str] = None
    nvidia_message: str
