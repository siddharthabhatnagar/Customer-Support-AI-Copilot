"""Realistic mock ticket dataset representing diverse B2B and B2C customer support scenarios."""
from typing import List, Dict, Any

MOCK_TICKETS: List[Dict[str, Any]] = [
    {
        "id": "TCK-101",
        "customer_name": "Marcus Vance",
        "customer_email": "marcus.vance@finflow.io",
        "company": "FinFlow Payments",
        "customer_tier": "Enterprise",
        "subject": "CRITICAL: Stripe webhook signature verification failing with HTTP 400 in production",
        "body": (
            "Hi team, our production webhook endpoint started failing all incoming Stripe payment events "
            "about 45 minutes ago with 'Invalid Signature: HMAC mismatch'. Over 350 transactions are currently stuck "
            "in unverified pending state. We verified the webhook signing secret in our dashboard (`whsec_981a...`) "
            "and deployed no recent code changes. Could this be a clock drift issue on your ingress or raw payload mutation? "
            "Please investigate immediately, our CFO is breathing down our necks!"
        ),
        "created_at": "2026-10-21T09:15:00Z",
        "status": "Open",
        "priority": "Urgent",
        "is_triaged": False,
    },
    {
        "id": "TCK-102",
        "customer_name": "Elena Rostova",
        "customer_email": "elena@lumina-analytics.com",
        "company": "Lumina Analytics",
        "customer_tier": "Pro",
        "subject": "Double charged for Annual Pro Plan after updating company corporate credit card",
        "body": (
            "Hello Support, I updated our billing corporate credit card yesterday because our old card was expiring. "
            "This morning I reviewed our Chase statement and noticed TWO separate transactions of $2,400.00 each on invoice #INV-8891. "
            "Our company account is now overdrafting its daily threshold. We need one of the $2,400 charges refunded immediately "
            "and an updated receipt. Please confirm the refund will take no longer than 48 hours."
        ),
        "created_at": "2026-10-21T09:45:00Z",
        "status": "Open",
        "priority": "High",
        "is_triaged": False,
    },
    {
        "id": "TCK-103",
        "customer_name": "David Chen",
        "customer_email": "dchen@nexushealth.org",
        "company": "Nexus Health Corp",
        "customer_tier": "Enterprise",
        "subject": "EMERGENCY: Entire company locked out - SAML Assertion Invalid on Okta SSO",
        "body": (
            "We have an emergency. None of our 450 clinical staff can log into the electronic records dashboard this morning. "
            "When users try to authenticate via our Okta SSO tenant, they are greeted with 'SAML Assertion Invalid (Code: SEC-500)'. "
            "I checked our Okta app integration and noticed our X.509 signing certificate rolled over at midnight. "
            "How do we update the cert in your system when we cannot even log into the admin portal? "
            "Is there an emergency bypass URL?"
        ),
        "created_at": "2026-10-21T10:02:00Z",
        "status": "Open",
        "priority": "Urgent",
        "is_triaged": False,
    },
    {
        "id": "TCK-104",
        "customer_name": "Sophie Moreau",
        "customer_email": "privacy@solardrive.eu",
        "company": "SolarDrive EU",
        "customer_tier": "Pro",
        "subject": "GDPR Article 17 Right to Erasure request for departing employee data",
        "body": (
            "Dear Data Protection Team, on behalf of SolarDrive EU (Data Controller), we are exercising our right to erasure under "
            "Article 17 of the GDPR for former employee id 'USR-9021' (lucas.bernard@solardrive.eu). "
            "Please confirm deletion of all personal identifiers, activity logs, and IP history within the statutory 30-day window, "
            "and supply an official certificate of cryptographic deletion for our regulatory records."
        ),
        "created_at": "2026-10-21T10:30:00Z",
        "status": "Open",
        "priority": "Medium",
        "is_triaged": False,
    },
    {
        "id": "TCK-105",
        "customer_name": "Arjun Patel",
        "customer_email": "arjun@cloudbridge.io",
        "company": "CloudBridge",
        "customer_tier": "Standard",
        "subject": "Feature Request: Bulk user provisioning mutation for GraphQL API",
        "body": (
            "Hi team! We love using your platform. We are currently automating our workspace onboarding using your GraphQL API. "
            "Right now, we have to loop through `createUser` mutations individually which is relatively slow when provisioning 200+ users. "
            "Would it be possible to add a `bulkCreateUsers(input: [UserInput!]!)` mutation in your next schema release? "
            "Keep up the great work!"
        ),
        "created_at": "2026-10-21T11:00:00Z",
        "status": "Open",
        "priority": "Low",
        "is_triaged": False,
    },
    {
        "id": "TCK-106",
        "customer_name": "Tariq Al-Mansoor",
        "customer_email": "tariq@vertexmedia.ae",
        "company": "Vertex Media",
        "customer_tier": "Enterprise",
        "subject": "Redis cache latency spiking to 650ms during scheduled 10 AM batch jobs",
        "body": (
            "Hey Support, our analytics pipeline runs a daily batch aggregation at 10:00 AM UTC. For the past three days, "
            "we are observing severe latency spikes up to 650ms on redis `MGET` queries for our tenant partition. "
            "This is causing cascade timeouts on our client dashboards. Can you inspect memory fragmentation, check bigkeys, "
            "or help us flush the tenant partition cache? Ticket details attached."
        ),
        "created_at": "2026-10-21T11:20:00Z",
        "status": "Open",
        "priority": "High",
        "is_triaged": False,
    },
    {
        "id": "TCK-107",
        "customer_name": "Rachel Adams",
        "customer_email": "radams@acmewidgets.com",
        "company": "Acme Widgets",
        "customer_tier": "Pro",
        "subject": "Password reset verification emails not reaching our corporate email inbox",
        "body": (
            "Hello, three of our new hires on the @acmewidgets.com domain have tried requesting password reset links, "
            "but nothing is arriving in their Inboxes or Spam folders. Our IT administrator checked our Proofpoint email filter logs "
            "and asked if you could provide the sender IPs and domains so we can whitelist them on our gateway, or if you can send a manual temporary link."
        ),
        "created_at": "2026-10-21T11:45:00Z",
        "status": "Open",
        "priority": "High",
        "is_triaged": False,
    },
    {
        "id": "TCK-108",
        "customer_name": "Liam O'Connor",
        "customer_email": "liam@breezestudio.ie",
        "company": "Breeze Studio",
        "customer_tier": "Standard",
        "subject": "Requesting to downgrade from Pro to Starter tier before November renewal",
        "body": (
            "Hi, we need to scale back our expenses next quarter and would like to downgrade our subscription from Pro to Starter "
            "before our renewal on November 1st. I tried clicking 'Change Plan' in the dashboard but it said 'Contact Support to adjust your contract'. "
            "Can you assist with this transition and ensure we retain our existing project workspaces?"
        ),
        "created_at": "2026-10-21T12:10:00Z",
        "status": "Open",
        "priority": "Medium",
        "is_triaged": False,
    },
    {
        "id": "TCK-109",
        "customer_name": "Chloe Bennett",
        "customer_email": "chloe@apexlogistics.com",
        "company": "Apex Global Logistics",
        "customer_tier": "Enterprise",
        "subject": "HTTP 429 Rate Limit Exceeded on production sync despite Enterprise 10,000 req/min contract",
        "body": (
            "We are on an Enterprise contract paying for 10,000 req/min. However, since 11:30 AM today, our fleet tracking server "
            "is receiving repeated HTTP 429 'Too Many Requests' with header `Retry-After: 60`. "
            "Our request rate is only hovering around 2,400 req/min, which is well below our contracted threshold. "
            "Truck dispatching is currently stalled. Please unlock our rate limit immediately."
        ),
        "created_at": "2026-10-21T12:35:00Z",
        "status": "Open",
        "priority": "Urgent",
        "is_triaged": False,
    },
    {
        "id": "TCK-110",
        "customer_name": "Kenji Sato",
        "customer_email": "ksato@cyberguard.jp",
        "company": "CyberGuard Tokyo",
        "customer_tier": "Enterprise",
        "subject": "Urgent security notification: Suspicious IP login alerts on admin service account",
        "body": (
            "Security Team: We detected anomalous authentication attempts on our primary admin service account "
            "originating from unfamiliar IP addresses in a different geography over the past 3 hours. "
            "We have already rotated our API keys on our end. Can you terminate all active OAuth sessions and provide the full audit log "
            "for the last 24 hours so our incident response team can trace potential compromise?"
        ),
        "created_at": "2026-10-21T13:00:00Z",
        "status": "Open",
        "priority": "Urgent",
        "is_triaged": False,
    },
    {
        "id": "TCK-111",
        "customer_name": "Emily Watson",
        "customer_email": "emily@designcraft.co",
        "company": "DesignCraft Co",
        "customer_tier": "Standard",
        "subject": "How can I export monthly analytics reports to PDF format?",
        "body": (
            "Hi there! Quick question - I see the button to export our monthly customer analytics data to CSV, "
            "but my executive team prefers a clean formatted PDF summary. Is there an export to PDF feature available, "
            "or a recommended browser print stylesheet setting that doesn't cut off the graph legends? Thanks!"
        ),
        "created_at": "2026-10-21T13:20:00Z",
        "status": "Open",
        "priority": "Low",
        "is_triaged": False,
    },
    {
        "id": "TCK-112",
        "customer_name": "Carlos Gomez",
        "customer_email": "carlos@fintechscale.mx",
        "company": "FinTech Scale",
        "customer_tier": "Pro",
        "subject": "Minor bug: Step 4 'Invite Team Members' hyperlink is broken on the onboarding checklist",
        "body": (
            "Good afternoon, just wanted to report a small bug we noticed. When new managers click Step 4 on the onboarding modal "
            "('Invite Team Members'), it redirects to a 404 page at `/app/team/invite-new` instead of `/app/settings/team`. "
            "Not a blocking issue for us as we found the button under Settings, but figured your UX team would want to fix the link."
        ),
        "created_at": "2026-10-21T13:40:00Z",
        "status": "Open",
        "priority": "Low",
        "is_triaged": False,
    }
]
