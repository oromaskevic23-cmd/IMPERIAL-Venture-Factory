"""Read-only classification of public issue forms; no pricing, CRM write or release authority."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SENSITIVE = [
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.I),
    re.compile(r"\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9_]{12,})\b"),
    re.compile(r"(?:authorization|api[_ -]?key|client[_ -]?secret)\s*[:=]\s*(?:bearer\s+)?[A-Za-z0-9_-]{8,}", re.I),
]
MARKERS = (
    "What should be assessed?",
    "Public, non-confidential description of the problem",
    "Expected first deliverable",
    "Public issue privacy and scope confirmation",
)
SCOPE_OPTIONS = {
    "One webhook or API integration", "One CRM / workflow automation",
    "Uncertain — need scoping",
}
DELIVERABLE_OPTIONS = {
    "Diagnostic report and reproducible synthetic test",
    "Audit plus implementation quote", "Scope discussion first",
}
CONSENT = (
    "- [x] I understand this issue is public and contains no secrets, personal data, payment details, or confidential material.",
    "- [x] I understand any price, delivery and live system access require separate human agreement and explicit approval.",
)


def complete_form(body: str) -> bool:
    """Require the actual GitHub form sections, in order, and nonempty answers.

    This validates structure, not the identity, truthfulness, or privacy of a sender.
    """
    lines = body.splitlines()
    headings = [(i, line.strip()[4:].strip()) for i, line in enumerate(lines)
                if line.strip().startswith("### ")]
    if [heading for _, heading in headings] != list(MARKERS):
        return False
    sections = []
    for pos, (start, _) in enumerate(headings):
        end = headings[pos + 1][0] if pos + 1 < len(headings) else len(lines)
        sections.append("\n".join(lines[start + 1:end]).strip())
    symptom = sections[1]
    if (sections[0] not in SCOPE_OPTIONS or sections[2] not in DELIVERABLE_OPTIONS
            or len(symptom) < 8 or symptom.casefold() in {"_no response_", "none", "n/a"}):
        return False
    consent_lines = {line.strip() for line in sections[3].splitlines()}
    return all(item in consent_lines for item in CONSENT)


def triage(payload: dict) -> dict:
    issue = payload.get("issue", {})
    if not isinstance(issue, dict) or issue.get("pull_request") is not None:
        return {"decision": "IGNORE", "reply_allowed": False}
    title = issue.get("title", "")
    body = issue.get("body", "")
    if not isinstance(title, str) or not title.startswith("[Audit request]"):
        return {"decision": "IGNORE", "reply_allowed": False}
    if not isinstance(body, str) or len(body) > 8000 or len(title) > 250 or any(p.search(title + "\n" + body) for p in SENSITIVE):
        return {"decision": "PRIVACY_REVIEW_REQUIRED", "reply_allowed": False}
    if len(title.removeprefix("[Audit request]").strip()) < 3 or not complete_form(body):
        return {"decision": "SCOPE_REVIEW_REQUIRED", "reply_allowed": False}
    return {"decision": "PUBLIC_ENQUIRY_RECEIVED", "reply_allowed": True}


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("USAGE: triage.py GITHUB_EVENT_JSON_PATH")
    p = Path(sys.argv[1])
    if p.is_symlink() or p.stat().st_size > 1024 * 1024:
        raise SystemExit("EVENT_FILE_REJECTED")
    event = json.loads(p.read_text(encoding="utf-8"))
    print(json.dumps(triage(event), sort_keys=True))


if __name__ == "__main__":
    main()
