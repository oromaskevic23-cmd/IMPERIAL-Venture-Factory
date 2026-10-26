"""Fail-closed, OFFLINE evidence-metadata gate evaluator.

This library NEVER advances production state, verifies signatures, deploys,
trades, accepts payments, sends messages or transfers IP. A 'ready_for_review'
decision only means required metadata is present. External Guardian Core,
CYBER HAK, Approval Gateway and human reviews remain mandatory.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Mapping, Optional

STAGES = (
    "IDEA", "DISCOVERY", "VALIDATED", "BUILD", "QA",
    "PILOT", "RELEASED", "EXIT_READY", "SOLD",
)

EVIDENCE = {
    "DISCOVERY": ("research_brief", "scope_budget"),
    "VALIDATED": ("customer_interviews", "validation_summary"),
    "BUILD": ("product_spec", "architecture_adr", "threat_model"),
    "QA": ("build_proof", "unit_integration_tests", "artifact_digest"),
    "PILOT": ("independent_qa", "privacy_review", "pilot_terms", "e2e_proof"),
    "RELEASED": ("security_review", "release_acceptance", "rollback_rehearsal"),
    "EXIT_READY": ("ip_audit", "finance_disclosure", "transfer_runbook"),
    "SOLD": ("signed_agreement", "settlement_verification", "transfer_acceptance"),
}

HUMAN_APPROVAL_REQUIRED = frozenset({
    "BUILD", "PILOT", "RELEASED", "EXIT_READY", "SOLD"
})
INDEPENDENT_REVIEW_REQUIRED = frozenset({
    "QA", "PILOT", "RELEASED", "EXIT_READY", "SOLD"
})
HEX_SHA256 = re.compile(r"^[a-fA-F0-9]{64}$")


@dataclass(frozen=True)
class GateDecision:
    ready_for_review: bool
    current: str
    requested: str
    missing: tuple[str, ...]
    reasons: tuple[str, ...]
    notice: str = (
        "Metadata readiness only: no signature, evidence authenticity, "
        "authority, or production outcome verified; no state changed."
    )


def evaluate_transition(
    current: str,
    requested: str,
    evidence: Optional[Mapping[str, str]] = None,
    approval_reference: Optional[str] = None,
    author_id: Optional[str] = None,
    reviewer_id: Optional[str] = None,
) -> GateDecision:
    """Evaluate next-step eligibility using formatted evidence hashes only.

    A SHA-256-looking value is a POINTER not cryptographic proof of anything.
    Approval references are metadata; real authority must be checked externally.
    """
    reasons: list[str] = []
    missing: list[str] = []
    if current not in STAGES or requested not in STAGES:
        return GateDecision(False, current, requested, (), ("UNKNOWN_STAGE",))
    if STAGES.index(requested) != STAGES.index(current) + 1:
        return GateDecision(False, current, requested, (), ("NON_SEQUENTIAL_TRANSITION",))
    if not isinstance(evidence, Mapping):
        evidence = {}
    for field in EVIDENCE.get(requested, ()):
        if not isinstance(evidence.get(field), str) or not HEX_SHA256.fullmatch(evidence[field]):
            missing.append(field)
    if missing:
        reasons.append("EVIDENCE_DIGEST_METADATA_MISSING")
    if requested in HUMAN_APPROVAL_REQUIRED and (
        not isinstance(approval_reference, str)
        or not approval_reference.strip()
    ):
        reasons.append("HUMAN_APPROVAL_REFERENCE_REQUIRED")
    if requested in INDEPENDENT_REVIEW_REQUIRED and (
        not isinstance(author_id, str) or not author_id.strip()
        or not isinstance(reviewer_id, str) or not reviewer_id.strip()
        or author_id.strip() == reviewer_id.strip()
    ):
        reasons.append("INDEPENDENT_REVIEW_METADATA_REQUIRED")
    return GateDecision(
        not reasons, current, requested, tuple(missing), tuple(reasons)
    )
