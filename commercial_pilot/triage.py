"""Read-only classification of public issue forms; no pricing, CRM write or release authority."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SENSITIVE = [
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


def triage(payload: dict) -> dict:
    issue = payload.get("issue", {})
    if not isinstance(issue, dict) or issue.get("pull_request") is not None:
        return {"decision": "IGNORE", "reply_allowed": False}
    title = issue.get("title", "")
    body = issue.get("body", "")
    if not isinstance(title, str) or not title.startswith("[Audit request]"):
        return {"decision": "IGNORE", "reply_allowed": False}
    if not isinstance(body, str) or len(body) > 8000 or any(p.search(body) for p in SENSITIVE):
        return {"decision": "PRIVACY_REVIEW_REQUIRED", "reply_allowed": False}
    if not all(marker in body for marker in MARKERS):
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
