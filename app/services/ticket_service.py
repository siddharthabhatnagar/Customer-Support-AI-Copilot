"""Ticket Service handling in-memory ticket management and triage workflows."""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from app.data.mock_tickets import MOCK_TICKETS
from app.models.schemas import Ticket, TicketCreateRequest, TriageResult
from app.services.ai_service import ai_service

class TicketService:
    def __init__(self):
        self.tickets: Dict[str, Ticket] = {}
        self._seed_mock_tickets()

    def _seed_mock_tickets(self):
        """Populate initial mock tickets."""
        for raw in MOCK_TICKETS:
            ticket = Ticket(
                id=raw["id"],
                customer_name=raw["customer_name"],
                customer_email=raw["customer_email"],
                company=raw.get("company", "Acme"),
                customer_tier=raw.get("customer_tier", "Standard"),
                subject=raw["subject"],
                body=raw["body"],
                created_at=raw["created_at"],
                status=raw.get("status", "Open"),
                priority=raw.get("priority", "Medium"),
                is_triaged=raw.get("is_triaged", False)
            )
            self.tickets[ticket.id] = ticket

        # Pre-triage first 3 tickets so user immediately sees rich AI data on first load!
        for pre_id in ["TCK-101", "TCK-102", "TCK-103"]:
            if pre_id in self.tickets:
                self.triage_ticket(pre_id)

    def list_tickets(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Ticket]:
        items = list(self.tickets.values())
        if status and status.lower() != "all":
            items = [t for t in items if t.status.lower() == status.lower()]
        if priority and priority.lower() != "all":
            items = [t for t in items if t.priority.lower() == priority.lower()]
        if category and category.lower() != "all":
            items = [t for t in items if (t.category or "").lower() == category.lower()]
        if search and search.strip():
            q = search.lower().strip()
            items = [
                t for t in items
                if q in t.subject.lower()
                or q in t.body.lower()
                or q in t.customer_name.lower()
                or q in t.id.lower()
                or q in t.company.lower()
            ]
        # Return sorted by ID or date
        return sorted(items, key=lambda t: t.id)

    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        return self.tickets.get(ticket_id)

    def create_ticket(self, req: TicketCreateRequest) -> Ticket:
        new_id = f"TCK-{len(self.tickets) + 101}"
        ticket = Ticket(
            id=new_id,
            customer_name=req.customer_name,
            customer_email=req.customer_email,
            company=req.company or "Acme Corp",
            customer_tier=req.customer_tier or "Standard",
            subject=req.subject,
            body=req.body,
            created_at=datetime.utcnow().isoformat() + "Z",
            status="Open",
            priority=req.priority or "Medium",
            is_triaged=False
        )
        self.tickets[ticket.id] = ticket
        return ticket

    def triage_ticket(self, ticket_id: str) -> Optional[TriageResult]:
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return None

        result = ai_service.full_triage(ticket)

        # Update ticket model
        ticket.category = result.classification.category
        ticket.subcategory = result.classification.subcategory
        ticket.priority = result.classification.priority
        ticket.tags = result.classification.suggested_tags
        ticket.sentiment = result.sentiment.sentiment
        ticket.sentiment_score = result.sentiment.score
        ticket.churn_risk = result.sentiment.churn_risk
        ticket.summary = result.summary
        ticket.escalation = result.escalation
        ticket.resolution_draft = result.rag_draft
        ticket.is_triaged = True

        if result.escalation.escalate:
            ticket.status = "Escalated"

        return result

    def triage_all(self) -> Dict[str, Any]:
        """Triage all currently untriaged tickets."""
        count = 0
        for ticket in self.tickets.values():
            if not ticket.is_triaged:
                self.triage_ticket(ticket.id)
                count += 1
        return {"triaged_count": count, "total_tickets": len(self.tickets)}

    def resolve_ticket(self, ticket_id: str) -> Optional[Ticket]:
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return None
        ticket.status = "Resolved"
        return ticket

ticket_service = TicketService()
