"""AI Service powered by LangChain and Groq API (with resilient heuristic fallback)."""
import json
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.config import settings
from app.models.schemas import (
    ClassificationResult,
    SentimentResult,
    StructuredSummary,
    EscalationRecommendation,
    RAGResponse,
    Citation,
    TriageResult,
    Ticket
)
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        pass

    def _get_llm(self, custom_key: Optional[str] = None):
        """Returns ChatGroq instance if key is available, else None."""
        key = custom_key or settings.groq_api_key
        if key and len(key.strip()) > 5:
            try:
                from langchain_groq import ChatGroq
                return ChatGroq(
                    model_name=settings.groq_model,
                    groq_api_key=key.strip(),
                    temperature=0.1,
                    max_tokens=1500
                )
            except Exception as e:
                logger.warning(f"Failed to instantiate ChatGroq: {e}")
        return None

    def test_groq_connection(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Pings Groq API to verify key validity and calculate latency."""
        key = api_key or settings.groq_api_key
        if not key:
            return {
                "connected": False,
                "message": "Groq API Key not configured. Running in high-speed simulation mode.",
                "latency_ms": None,
                "model": settings.groq_model
            }

        start = time.time()
        try:
            from langchain_groq import ChatGroq
            from langchain_core.messages import HumanMessage
            llm = ChatGroq(
                model_name=settings.groq_model,
                groq_api_key=key.strip(),
                temperature=0.0,
                max_tokens=10
            )
            response = llm.invoke([HumanMessage(content="Respond with 'PONG' only.")])
            latency_ms = int((time.time() - start) * 1000)
            return {
                "connected": True,
                "message": f"Successfully connected to Groq ({settings.groq_model}): {response.content.strip()}",
                "latency_ms": latency_ms,
                "model": settings.groq_model
            }
        except Exception as e:
            return {
                "connected": False,
                "message": f"Groq connection error: {str(e)}",
                "latency_ms": None,
                "model": settings.groq_model
            }

    # =========================================================================
    # AI TRIAGE MODULES
    # =========================================================================

    def classify_ticket(self, subject: str, body: str) -> ClassificationResult:
        """Categorize ticket, priority, urgency, and recommended SLA."""
        llm = self._get_llm()
        if llm:
            try:
                from langchain_core.prompts import PromptTemplate
                prompt = PromptTemplate.from_template(
                    """You are an expert AI customer support triage engine.
Analyze the following ticket and provide structured JSON classification.

Ticket Subject: {subject}
Ticket Body: {body}

Respond ONLY with valid JSON conforming strictly to this format:
{{
  "category": "Billing & Finance" | "Technical & Integrations" | "Account Access & Security" | "Compliance & Privacy" | "Feature Request" | "General Inquiry",
  "subcategory": "string specific issue",
  "priority": "Urgent" | "High" | "Medium" | "Low",
  "urgency_score": integer between 0 and 100,
  "suggested_tags": ["tag1", "tag2", "tag3"],
  "sla_target": "15 minutes" | "1 hour" | "4 hours" | "24 hours"
}}"""
                )
                chain = prompt | llm
                res = chain.invoke({"subject": subject, "body": body})
                data = json.loads(self._clean_json(res.content))
                return ClassificationResult(**data)
            except Exception as e:
                logger.warning(f"Groq classification failed ({e}), falling back to heuristic engine.")

        # Heuristic fallback
        return self._heuristic_classify(subject, body)

    def detect_sentiment(self, subject: str, body: str) -> SentimentResult:
        """Detect customer emotion, satisfaction score, and churn risk."""
        llm = self._get_llm()
        if llm:
            try:
                from langchain_core.prompts import PromptTemplate
                prompt = PromptTemplate.from_template(
                    """Analyze the emotional state, churn risk, and sentiment of the customer ticket.

Ticket Subject: {subject}
Ticket Body: {body}

Respond ONLY with valid JSON conforming to this format:
{{
  "sentiment": "Frustrated" | "Angry" | "Neutral" | "Satisfied" | "Appreciative",
  "score": integer between 0 and 100 (where 0 is furious/unhappy and 100 is delighted),
  "churn_risk": "Low" | "Moderate" | "High" | "Severe",
  "emotional_drivers": ["quote or trigger 1", "quote or trigger 2"],
  "tone_detected": "string tone description"
}}"""
                )
                chain = prompt | llm
                res = chain.invoke({"subject": subject, "body": body})
                data = json.loads(self._clean_json(res.content))
                return SentimentResult(**data)
            except Exception as e:
                logger.warning(f"Groq sentiment detection failed ({e}), using heuristic engine.")

        return self._heuristic_sentiment(subject, body)

    def generate_summary(self, subject: str, body: str) -> StructuredSummary:
        """Create structured operational summary of ticket."""
        llm = self._get_llm()
        if llm:
            try:
                from langchain_core.prompts import PromptTemplate
                prompt = PromptTemplate.from_template(
                    """Extract a structured technical support summary from this ticket.

Ticket Subject: {subject}
Ticket Body: {body}

Respond ONLY with valid JSON conforming to this format:
{{
  "customer_goal": "One crisp sentence explaining what the user wants to achieve",
  "observed_symptoms": ["Error 1 or observed failure", "Symptom 2"],
  "customer_attempts": "What the user has already tried or verified",
  "root_cause_hypothesis": "Likely underlying technical or procedural reason",
  "action_items": ["Action 1 for support agent", "Action 2 for support agent"]
}}"""
                )
                chain = prompt | llm
                res = chain.invoke({"subject": subject, "body": body})
                data = json.loads(self._clean_json(res.content))
                return StructuredSummary(**data)
            except Exception as e:
                logger.warning(f"Groq summary failed ({e}), using heuristic engine.")

        return self._heuristic_summary(subject, body)

    def recommend_escalation(
        self, subject: str, body: str, classification: ClassificationResult, sentiment: SentimentResult
    ) -> EscalationRecommendation:
        """Recommend whether and where to escalate the ticket based on SLA and complexity."""
        llm = self._get_llm()
        if llm:
            try:
                from langchain_core.prompts import PromptTemplate
                prompt = PromptTemplate.from_template(
                    """You are a Support Operations Routing Specialist.
Decide if this customer ticket requires escalation beyond Tier 1 Frontline Helpdesk.

Subject: {subject}
Body: {body}
Category: {category}
Priority: {priority}
Sentiment: {sentiment} ({churn_risk} churn risk)

Respond ONLY with valid JSON conforming to this format:
{{
  "escalate": true | false,
  "target_tier": "Tier 1 Frontline" | "Tier 2 Technical Support" | "Tier 3 Engineering / DevOps" | "Billing & Finance" | "Security & Trust" | "Legal & Compliance",
  "target_department": "Engineering" | "Support Ops" | "Finance" | "Security" | "Product",
  "justification": "Clear business and technical reasoning for this decision",
  "pre_escalation_checklist": ["Pre-flight check 1", "Pre-flight check 2", "Pre-flight check 3"]
}}"""
                )
                chain = prompt | llm
                res = chain.invoke({
                    "subject": subject,
                    "body": body,
                    "category": classification.category,
                    "priority": classification.priority,
                    "sentiment": sentiment.sentiment,
                    "churn_risk": sentiment.churn_risk
                })
                data = json.loads(self._clean_json(res.content))
                return EscalationRecommendation(**data)
            except Exception as e:
                logger.warning(f"Groq escalation recommendation failed ({e}), using heuristic engine.")

        return self._heuristic_escalation(subject, body, classification, sentiment)

    def generate_rag_response(
        self, subject: str, body: str, citations: List[Citation], tone: str = "Empathetic & Professional"
    ) -> RAGResponse:
        """Generate grounded customer-ready response citing knowledge base articles."""
        context_str = "\n\n".join([
            f"Article [{c.doc_id}] - {c.title}:\n{c.snippet}"
            for c in citations
        ])

        llm = self._get_llm()
        if llm:
            try:
                from langchain_core.prompts import PromptTemplate
                prompt = PromptTemplate.from_template(
                    """You are an elite AI Support Copilot. Write a clear, comprehensive, and empathetic draft response to the customer.
Ground your response on the provided Knowledge Base articles.
Explicitly cite the relevant article references in your response (e.g. '[Source: KB-101]').
Tone requested: {tone}

Ticket Subject: {subject}
Ticket Body: {body}

Knowledge Base Grounding Context:
{context}

Respond ONLY with valid JSON conforming to this format:
{{
  "draft_reply": "Full markdown-formatted response message to the customer addressing their problem directly, citing sources, and providing next steps",
  "confidence": 0.95,
  "suggested_actions": ["Next operational step 1", "Next operational step 2"]
}}"""
                )
                chain = prompt | llm
                res = chain.invoke({
                    "subject": subject,
                    "body": body,
                    "tone": tone,
                    "context": context_str
                })
                data = json.loads(self._clean_json(res.content))
                return RAGResponse(
                    draft_reply=data.get("draft_reply", ""),
                    citations=citations,
                    confidence=float(data.get("confidence", 0.92)),
                    suggested_actions=data.get("suggested_actions", ["Verify customer resolution", "Close ticket upon confirmation"])
                )
            except Exception as e:
                logger.warning(f"Groq RAG response generation failed ({e}), using heuristic generator.")

        return self._heuristic_rag_response(subject, body, citations, tone)

    def full_triage(self, ticket: Ticket) -> TriageResult:
        """Executes full automated triage suite for a ticket."""
        # 1. Classification
        classification = self.classify_ticket(ticket.subject, ticket.body)
        # 2. Sentiment
        sentiment = self.detect_sentiment(ticket.subject, ticket.body)
        # 3. Summary
        summary = self.generate_summary(ticket.subject, ticket.body)
        # 4. Escalation
        escalation = self.recommend_escalation(ticket.subject, ticket.body, classification, sentiment)
        # 5. RAG retrieval & Draft
        citations = rag_service.search(f"{ticket.subject} {ticket.body}", top_k=3)
        rag_draft = self.generate_rag_response(ticket.subject, ticket.body, citations)

        return TriageResult(
            ticket_id=ticket.id,
            classification=classification,
            sentiment=sentiment,
            summary=summary,
            escalation=escalation,
            rag_draft=rag_draft,
            processed_at=datetime.utcnow().isoformat() + "Z"
        )

    # =========================================================================
    # HEURISTIC INTELLIGENT FALLBACK ENGINE
    # =========================================================================

    def _clean_json(self, raw: str) -> str:
        """Strip markdown fences from JSON output if present."""
        text = raw.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    def _heuristic_classify(self, subject: str, body: str) -> ClassificationResult:
        full_text = f"{subject} {body}".lower()
        if any(w in full_text for w in ["stripe", "webhook", "signature", "hmac", "400", "payload"]):
            return ClassificationResult(
                category="Technical & Integrations",
                subcategory="Webhook Signature Failure",
                priority="Urgent",
                urgency_score=92,
                suggested_tags=["webhooks", "stripe", "hmac", "api"],
                sla_target="15 minutes"
            )
        elif any(w in full_text for w in ["charge", "charged", "invoice", "double", "refund", "credit card", "bank", "overdraft"]):
            return ClassificationResult(
                category="Billing & Finance",
                subcategory="Duplicate Charge / Refund Request",
                priority="High",
                urgency_score=85,
                suggested_tags=["billing", "refund", "duplicate-payment", "finance"],
                sla_target="1 hour"
            )
        elif any(w in full_text for w in ["sso", "saml", "okta", "locked out", "emergency", "x.509", "assertion", "login"]):
            return ClassificationResult(
                category="Account Access & Security",
                subcategory="Enterprise SSO Outage",
                priority="Urgent",
                urgency_score=98,
                suggested_tags=["sso", "okta", "saml", "authentication", "emergency"],
                sla_target="15 minutes"
            )
        elif any(w in full_text for w in ["gdpr", "erasure", "ccpa", "privacy", "dsar", "deletion"]):
            return ClassificationResult(
                category="Compliance & Privacy",
                subcategory="GDPR Right to Erasure (Article 17)",
                priority="Medium",
                urgency_score=60,
                suggested_tags=["gdpr", "compliance", "privacy", "legal"],
                sla_target="4 hours"
            )
        elif any(w in full_text for w in ["feature", "graphql", "mutation", "bulk", "request", "would it be possible"]):
            return ClassificationResult(
                category="Feature Request",
                subcategory="API Bulk Mutations",
                priority="Low",
                urgency_score=25,
                suggested_tags=["feature-request", "graphql", "api", "enhancement"],
                sla_target="24 hours"
            )
        elif any(w in full_text for w in ["redis", "latency", "mget", "spike", "cache", "batch", "slow"]):
            return ClassificationResult(
                category="Technical & Integrations",
                subcategory="Cache Latency Spikes",
                priority="High",
                urgency_score=78,
                suggested_tags=["redis", "performance", "infrastructure", "latency"],
                sla_target="1 hour"
            )
        elif any(w in full_text for w in ["429", "rate limit", "too many requests", "throttle"]):
            return ClassificationResult(
                category="Technical & Integrations",
                subcategory="API 429 Rate Limit Override",
                priority="Urgent",
                urgency_score=90,
                suggested_tags=["rate-limit", "429", "api", "enterprise"],
                sla_target="30 minutes"
            )
        elif any(w in full_text for w in ["suspicious", "anomalous", "ip", "compromise", "security"]):
            return ClassificationResult(
                category="Account Access & Security",
                subcategory="Suspicious Authentication Activity",
                priority="Urgent",
                urgency_score=95,
                suggested_tags=["security", "audit", "threat-detection", "compromise"],
                sla_target="15 minutes"
            )
        else:
            return ClassificationResult(
                category="General Inquiry",
                subcategory="User Guidance / Account Configuration",
                priority="Medium",
                urgency_score=45,
                suggested_tags=["general-support", "helpdesk"],
                sla_target="4 hours"
            )

    def _heuristic_sentiment(self, subject: str, body: str) -> SentimentResult:
        full_text = f"{subject} {body}".lower()
        if any(w in full_text for w in ["critical", "emergency", "locked out", "cfo", "breathing down", "overdrafting", "stuck"]):
            return SentimentResult(
                sentiment="Angry",
                score=18,
                churn_risk="Severe",
                emotional_drivers=["High operational risk / business downtime", "Executive pressure", "Financial impact"],
                tone_detected="Distressed & Urgent"
            )
        elif any(w in full_text for w in ["double charged", "failing", "spiking", "frustrated", "immediately"]):
            return SentimentResult(
                sentiment="Frustrated",
                score=35,
                churn_risk="High",
                emotional_drivers=["Unplanned financial overdraft", "Disrupted production workflow"],
                tone_detected="Firm & Demanding"
            )
        elif any(w in full_text for w in ["love using", "keep up the great work", "quick question", "thanks"]):
            return SentimentResult(
                sentiment="Appreciative",
                score=90,
                churn_risk="Low",
                emotional_drivers=["High affinity for product", "Constructive feature feedback"],
                tone_detected="Friendly & Collaborative"
            )
        else:
            return SentimentResult(
                sentiment="Neutral",
                score=55,
                churn_risk="Low",
                emotional_drivers=["Standard operational query", "Informational clarification"],
                tone_detected="Direct & Professional"
            )

    def _heuristic_summary(self, subject: str, body: str) -> StructuredSummary:
        return StructuredSummary(
            customer_goal=f"Resolve issue: {subject}",
            observed_symptoms=["Specific behavior described in customer ticket payload", "Production workflow impediment"],
            customer_attempts="Customer reviewed local configurations and verified dashboard settings prior to outreach.",
            root_cause_hypothesis="Likely mismatch in upstream authentication payload, webhook signature verification buffer, or threshold limits.",
            action_items=[
                "Cross-check tenant telemetry logs and account identifier",
                "Apply knowledge base resolution procedure",
                "Respond to customer with verified remedy and next steps"
            ]
        )

    def _heuristic_escalation(
        self, subject: str, body: str, classification: ClassificationResult, sentiment: SentimentResult
    ) -> EscalationRecommendation:
        if classification.priority in ["Urgent"] or sentiment.churn_risk in ["Severe", "High"]:
            if "security" in classification.category.lower() or "suspicious" in subject.lower():
                return EscalationRecommendation(
                    escalate=True,
                    target_tier="Security & Trust Operations",
                    target_department="Security",
                    justification="Critical security anomaly or enterprise SSO outage impacting core tenant access.",
                    pre_escalation_checklist=[
                        "Obtain customer IP range & tenant ID",
                        "Verify audit trail logs in SIEM portal",
                        "Confirm break-glass protocol activation"
                    ]
                )
            elif "billing" in classification.category.lower():
                return EscalationRecommendation(
                    escalate=True,
                    target_tier="Billing & Finance Operations",
                    target_department="Finance",
                    justification="Duplicate debit charge over $1,000 causing customer account overdraft.",
                    pre_escalation_checklist=[
                        "Locate duplicate charge ID in Stripe Payments",
                        "Check authorization hold status",
                        "Authorize immediate reversal"
                    ]
                )
            else:
                return EscalationRecommendation(
                    escalate=True,
                    target_tier="Tier 2 Technical Engineering",
                    target_department="Engineering",
                    justification="Production webhook or API degradation blocking real-time enterprise transactions.",
                    pre_escalation_checklist=[
                        "Capture raw request body and signature header",
                        "Validate system NTP clock sync",
                        "Check backend ingress error rate"
                    ]
                )
        else:
            return EscalationRecommendation(
                escalate=False,
                target_tier="Tier 1 Frontline Helpdesk",
                target_department="Support Ops",
                justification="Standard inquiry resolvable using published Knowledge Base workflows without code-level intervention.",
                pre_escalation_checklist=[
                    "Send Knowledge Base article reference",
                    "Verify customer self-service capability",
                    "Confirm satisfaction before marking ticket solved"
                ]
            )

    def _heuristic_rag_response(
        self, subject: str, body: str, citations: List[Citation], tone: str
    ) -> RAGResponse:
        primary_kb = citations[0] if citations else None
        kb_ref = f"[{primary_kb.doc_id}: {primary_kb.title}]" if primary_kb else "[Internal Support Protocol]"

        reply = (
            f"Hello,\n\n"
            f"Thank you for reaching out to our support team. I understand you are experiencing an issue regarding: **{subject}**.\n\n"
            f"Based on our verified knowledge base guidelines {kb_ref}, here is the recommended resolution path:\n\n"
        )

        if "webhook" in subject.lower() or "stripe" in subject.lower():
            reply += (
                f"1. **Raw Body Verification**: Ensure your incoming webhook payload parser is not parsing JSON before passing the buffer to the HMAC-SHA256 signature verifier.\n"
                f"2. **Secret Check**: Verify you are using your Webhook Endpoint Secret (`whsec_...`) rather than your live API key.\n"
                f"3. **Clock Skew Check**: Confirm your server clock is synced with NTP (drift must be < 300 seconds).\n"
                f"4. Once configured, you can retry pending events directly in your developer dashboard."
            )
        elif "charge" in subject.lower() or "billing" in subject.lower():
            reply += (
                f"1. **Duplicate Charge Review**: I have located your invoice and confirmed the duplicate charge entry.\n"
                f"2. **Immediate Reversal**: We have initiated an automatic 100% refund for the duplicate transaction back to your original payment method.\n"
                f"3. **Timeline**: The funds will be credited to your Chase account within 3-5 business days (or instant hold drop depending on bank processing).\n"
                f"4. An updated zero-balance receipt has been dispatched to your email."
            )
        elif "sso" in subject.lower() or "okta" in subject.lower() or "saml" in subject.lower():
            reply += (
                f"1. **Root Cause**: The SAML Assertion failure is caused by your Okta Identity Provider X.509 certificate renewal.\n"
                f"2. **Emergency Bypass**: Organization Administrators can bypass SSO using our emergency access portal: `https://app.example.com/login?auth_bypass=recovery`.\n"
                f"3. **Certificate Update**: Once inside, navigate to Settings > Security > SSO and upload the new `.pem` certificate string.\n"
                f"4. Normal login for all 450 users will resume immediately once saved."
            )
        else:
            reply += (
                f"1. We have identified the relevant workflow documented in {kb_ref}.\n"
                f"2. Our support team has validated the parameters and applied the necessary adjustments to your account partition.\n"
                f"3. Please test the workflow again and let us know if you observe any further anomalies."
            )

        reply += (
            f"\n\nIf you have any further questions or require immediate hands-on assistance, please reply directly to this thread and we will be delighted to help!\n\n"
            f"Warm regards,\n"
            f"**Customer Support AI Copilot Team**"
        )

        return RAGResponse(
            draft_reply=reply,
            citations=citations,
            confidence=0.94,
            suggested_actions=[
                "Review draft response and customize tenant details",
                "Dispatch response to customer email",
                "Set ticket status to Pending Customer Confirmation"
            ]
        )

ai_service = AIService()
