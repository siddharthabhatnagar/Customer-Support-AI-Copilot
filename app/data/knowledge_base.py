"""Knowledge Base dataset used by the RAG retrieval engine."""
from typing import List, Dict, Any

KNOWLEDGE_BASE_ARTICLES: List[Dict[str, Any]] = [
    {
        "id": "KB-101",
        "title": "Webhook Signature Verification and Stripe Integration Debugging",
        "category": "Technical & Integrations",
        "tags": ["webhooks", "stripe", "signatures", "hmac", "crypto", "api-errors"],
        "last_updated": "2026-09-15",
        "content": (
            "Overview: When processing webhook events from Stripe, PayPal, or internal services, "
            "incoming payloads must pass HMAC-SHA256 signature verification. "
            "Common Causes of Failure:\n"
            "1. Raw Body Mutation: Web framework JSON parsers (e.g. Express body-parser, FastAPI json middleware) "
            "modify whitespace or byte order before signature checks. Always verify using the unparsed raw byte payload.\n"
            "2. Secret Mismatch: Ensure you are using the specific Webhook Signing Secret (whsec_...) and not your API Secret Key (sk_live_...).\n"
            "3. Clock Skew: Signatures contain a timestamp header (`stripe-signature: t=...`). If your server clock drifts > 300 seconds, verification fails.\n"
            "4. Webhook Retries: Failed webhook attempts retry on exponential backoff up to 72 hours. Once resolved, trigger 'Resend event' in the developer dashboard.\n"
            "Recommended Resolution:\n"
            "- Inspect raw payload buffer before deserialization.\n"
            "- Verify system NTP server synchronization.\n"
            "- Test using Stripe CLI `stripe trigger payment_intent.succeeded`."
        )
    },
    {
        "id": "KB-102",
        "title": "Billing Invoicing, Duplicate Charges, and 48-Hour Refund Policy",
        "category": "Billing & Finance",
        "tags": ["billing", "refunds", "duplicate-charge", "invoice", "stripe", "credit-card"],
        "last_updated": "2026-10-01",
        "content": (
            "Policy & Refund Workflow:\n"
            "1. Duplicate Charges: If an invoice was charged twice due to card re-entry or temporary network double-post, "
            "our billing portal immediately voids the pending authorization hold or triggers an automatic reversal.\n"
            "2. Refund Timeline: Standard refunds take 3 to 5 business days to reflect on the customer's bank statement depending on their financial institution.\n"
            "3. Eligibility: Any accidental charge, unexpected plan auto-renewal reported within 14 days, or system outage compensation is eligible for 100% refund without penalty.\n"
            "4. Pro-Rated Adjustments: Upgrades or downgrades during an active billing cycle automatically apply credit balance towards the subsequent invoice.\n"
            "Support Agent Action:\n"
            "- Look up the customer in Stripe Billing by email or invoice number `inv_...`.\n"
            "- Check 'Payments' tab for duplicated charges.\n"
            "- Click 'Refund payment' with reason 'Duplicate charge'. Issue confirmation receipt to customer."
        )
    },
    {
        "id": "KB-103",
        "title": "Enterprise SSO, SAML 2.0 Certificate Renewal and Okta Setup",
        "category": "Account Access & Security",
        "tags": ["sso", "saml", "okta", "azure-ad", "certificates", "enterprise", "x509"],
        "last_updated": "2026-08-20",
        "content": (
            "Enterprise Single Sign-On (SSO) Guidelines:\n"
            "1. Expired X.509 Certificate: If users receive 'SAML Assertion Invalid' or 500 error when logging in via Okta or Azure AD, "
            "the Identity Provider's X.509 signing certificate has usually expired.\n"
            "2. Certificate Rollover Process:\n"
            "   a. Identity Provider admin downloads new signing cert (.cer or .pem) from Okta/Entra ID.\n"
            "   b. Admin navigates to Settings > Security > SSO > 'Update Certificate'.\n"
            "   c. Paste the new certificate string including `-----BEGIN CERTIFICATE-----` and `-----END CERTIFICATE-----`.\n"
            "   d. Zero downtime: Our platform supports secondary cert upload 30 days prior to expiration.\n"
            "3. Emergency Bypass: Org Admins can access via fallback emergency URL: `/login?auth_bypass=recovery` with break-glass MFA credentials.\n"
            "Support Agent Action:\n"
            "- Verify tenant domain status in Admin Console.\n"
            "- Provide the Customer IT Admin with the direct certificate upload link.\n"
            "- If urgent lockout affects > 100 users, elevate to Security Ops."
        )
    },
    {
        "id": "KB-104",
        "title": "API Rate Limits, Quota Tiers, and HTTP 429 Throttling Resolution",
        "category": "Technical & Integrations",
        "tags": ["api", "rate-limit", "429", "throttling", "enterprise-quota", "concurrency"],
        "last_updated": "2026-09-30",
        "content": (
            "API Rate Limiting Architecture:\n"
            "1. Default Limits:\n"
            "   - Free Tier: 60 requests/minute, burst up to 100.\n"
            "   - Pro Tier: 600 requests/minute, burst up to 1,200.\n"
            "   - Enterprise Tier: 10,000 requests/minute, custom concurrency up to 50,000.\n"
            "2. HTTP 429 Response Headers: Check `Retry-After: <seconds>`, `X-RateLimit-Limit`, and `X-RateLimit-Remaining`.\n"
            "3. Common Misconfiguration: Enterprise clients hitting 429 typically haven't generated a Dedicated Enterprise Production API Token, "
            "or are querying endpoints from an unverified staging key stuck on default tiers.\n"
            "Support Agent Action:\n"
            "- Inspect API key metadata in developer portal.\n"
            "- If customer is on Enterprise contract, ensure `tier_override` flag is enabled.\n"
            "- Recommend implementing exponential jitter backoff on the client."
        )
    },
    {
        "id": "KB-105",
        "title": "Email Deliverability, Corporate Whitelisting & Auth Password Resets",
        "category": "Account Access & Security",
        "tags": ["email", "deliverability", "spam", "whitelist", "password-reset", "auth", "mfa"],
        "last_updated": "2026-07-12",
        "content": (
            "Email Deliverability & Password Reset Failures:\n"
            "1. Corporate Gateways: Security appliances like Proofpoint, Mimecast, or Microsoft Defender often quarantine automated transactional emails "
            "or trigger one-time password links prematurely during automated URL sandbox scanning.\n"
            "2. Solutions for Corporate Customers:\n"
            "   - Whitelist sender domain `@auth.company.com` and IPs `198.51.100.0/24`.\n"
            "   - Enable 'Single-Use Link with Confirmation Button' to prevent URL pre-crawlers from expiring reset tokens.\n"
            "3. Manual Password Reset: Support agents can generate a secure 60-minute time-bound temporary reset link directly from the Admin Portal.\n"
            "Verification Requirements: Confirm requester identity via Slack Connect, verified corporate email, or secondary phone code before issuing manual reset links."
        )
    },
    {
        "id": "KB-106",
        "title": "Database Query Latency and Redis Cache Invalidation Protocol",
        "category": "Technical & Infrastructure",
        "tags": ["database", "redis", "latency", "cache", "performance", "slow-query"],
        "last_updated": "2026-09-05",
        "content": (
            "Latency Spikes & Redis Cache Diagnostics:\n"
            "1. High Latency (> 300ms) on batch operations is often caused by cache key fragmentation, big-key serialization locks, "
            "or missing composite indexes on tenant multi-tenant tables.\n"
            "2. Steps to Resolve:\n"
            "   - Review Slow Query Log in Datadog / Grafana.\n"
            "   - Check Redis memory usage with `INFO memory` and `redis-cli --bigkeys`.\n"
            "   - Flush partition cache: `POST /api/v2/cache/purge-tenant?tenant_id=...`\n"
            "3. Escalation: If query latency exceeds 2000ms for over 15 minutes, page the Infrastructure On-Call engineer immediately."
        )
    },
    {
        "id": "KB-107",
        "title": "GDPR, CCPA & Data Subject Access Request (DSAR) Compliance Workflow",
        "category": "Compliance & Privacy",
        "tags": ["gdpr", "ccpa", "privacy", "dsar", "data-export", "deletion", "compliance"],
        "last_updated": "2026-08-11",
        "content": (
            "Data Subject Access & Deletion Requests:\n"
            "1. Legal Timelines: GDPR and CCPA require complete data export or hard deletion within 30 calendar days.\n"
            "2. Automatic Export Tool: Users can export all workspace records under Account Settings > Privacy > 'Request Full Archive (JSON/ZIP)'.\n"
            "3. Erasure Procedure: Once identity is legally verified, trigger the GDPR Deletion pipeline in the Compliance Console. "
            "Audit logs are retained in anonymized hash format for 7 years to satisfy regulatory compliance.\n"
            "Support Action: Acknowledge request within 24 hours, tag ticket with `#compliance-gdpr`, and assign to Data Privacy Officer."
        )
    },
    {
        "id": "KB-108",
        "title": "Support Escalation Matrix, SLA Targets, and Tier Protocols",
        "category": "Operations & SLA",
        "tags": ["escalation", "sla", "priority", "tier1", "tier2", "security", "engineering"],
        "last_updated": "2026-10-10",
        "content": (
            "Support Escalation Matrix:\n"
            "1. Tier 1 (Helpdesk): General how-to questions, basic password reset assistance, billing receipts, account guidance. SLA: First response < 30 mins.\n"
            "2. Tier 2 (Technical Support): API errors, webhook signature issues, rate limit modifications, caching latency, integration troubleshooting. SLA: < 2 hours.\n"
            "3. Tier 3 (Engineering / DevOps): System bugs with reproducible stack traces, production database degradation, security vulnerabilities, infrastructure outage. SLA: < 15 mins.\n"
            "4. Billing & Legal Ops: Disputed charges > $1,000, contract amendments, GDPR compliance. SLA: < 4 hours.\n"
            "Escalation Criteria Checklist:\n"
            "- Step 1: Has customer provided minimal reproduction steps or logs?\n"
            "- Step 2: Have Tier 1 KB troubleshooting steps been attempted and documented?\n"
            "- Step 3: Is business revenue or active customer access blocked?\n"
            "If yes to Step 3, escalate immediately with High/Urgent priority."
        )
    }
]
