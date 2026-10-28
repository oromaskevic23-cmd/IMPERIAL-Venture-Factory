"""Fail-closed commercial intake: GitHub Issue -> CRM-SOFFT draft -> ASTRA handoff candidate.

Uses PostgreSQL through an injected DB-API connection. No automatic execution or approval.
The only database mutation is an idempotent, non-sensitive draft lead.
"""
import hashlib
import json
import re

REPO = "oromaskevic23-cmd/IMPERIAL-Venture-Factory"
WORKSPACE = "IMPERIAL-GLOBAL"
SOURCE = "GITHUB_ISSUES_IC_OFFER_001"
IDENT = re.compile(r"^[1-9][0-9]{0,12}$")


def receipt(issue):
    number = str(issue.get("number", ""))
    if not IDENT.fullmatch(number):
        raise ValueError("INVALID_ISSUE_NUMBER")
    if issue.get("repository") != REPO or issue.get("decision") != "PUBLIC_ENQUIRY_RECEIVED":
        raise ValueError("UNTRUSTED_SOURCE_OR_TRIAGE")
    if issue.get("author") == "oromaskevic23-cmd" or issue.get("test") is True:
        raise ValueError("OWNER_TEST_DENIED")
    if issue.get("state") != "open":
        raise ValueError("ISSUE_NOT_OPEN")
    return number, hashlib.sha256(
        json.dumps({"repo": REPO, "issue": number, "offer": "IC-OFFER-001"},
                   sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def intake(conn, issue, *, dry_run=True):
    number, digest = receipt(issue)
    source_ref = "github:" + REPO + "#" + number
    # Never store public issue body or customer PII in CRM; scope remains untrusted.
    draft = {
        "workspace_id": WORKSPACE,
        "demand_source": SOURCE,
        "source_ref": source_ref,
        "source_receipt_hash": digest,
        "need": "IC-OFFER-001: automation failure audit; pending human scope/privacy review",
        "state": "LEAD_CREATED",
    }
    if dry_run:
        return {"status": "DRY_RUN", "draft": draft, "next": "OWNER_SCOPE_REVIEW_REQUIRED"}
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO crm_sofft.lead_registry\n               (workspace_id,demand_source,source_ref,source_receipt_hash,need,state)\n               VALUES (%(workspace_id)s,%(demand_source)s,%(source_ref)s,\n                       %(source_receipt_hash)s,%(need)s,%(state)s)\n               ON CONFLICT (workspace_id,demand_source,source_receipt_hash) DO NOTHING\n               RETURNING lead_id""", draft
        )
        row = cur.fetchone()
    conn.commit()
    return {"status": "DRAFT_INSERTED" if row else "DUPLICATE_IGNORED",
            "source_ref": source_ref, "next": "OWNER_SCOPE_REVIEW_REQUIRED"}


def astra_handoff_candidate(issue, approval=None):
    """Produce a non-executable envelope; no dispatch without separately verified approval."""
    number, digest = receipt(issue)
    return {
        "type": "COMMERCIAL_SCOPE_REVIEW_CANDIDATE",
        "offer": "IC-OFFER-001",
        "source_ref": "github:" + REPO + "#" + number,
        "receipt_sha256": digest,
        "requested_orchestrator": "ASTRA",
        "routing": "HANTER_FEDERATED",
        "executor": "LEGION_NANO_CORE_AGENTS",
        "guardian": "NOT_EVALUATED",
        "ai_passport": "NOT_VERIFIED",
        "enterprise_skills": "NOT_VERIFIED",
        "approval_gateway": "NOT_APPROVED",
        "audit_ledger": "NOT_WRITTEN",
        "public_private_boundary": "ENFORCED_NO_CLIENT_CONTENT",
        "crypto_boundary": "NO_PAYMENTS",
        "dispatch_allowed": False,
        "approval_reference": None,
    }
