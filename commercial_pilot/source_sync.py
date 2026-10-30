"""Read-only authenticated-origin GitHub Issue discovery for IC-OFFER-001.

The CLI never opens a database, posts to customers, prices work, or dispatches agents.
Server-side callers may pass the returned sanitized records to federated_bridge.intake
using their own isolated, authorized DB-API connection.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path

from commercial_pilot.federated_bridge import REPO, WORKSPACE, SOURCE, receipt
from commercial_pilot.triage import triage

GITHUB_API = "https://api.github.com/repos/" + REPO
OWNER = REPO.split("/")[0]
MAX_RESPONSE = 1024 * 1024
EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
TEST_MARKERS = ("SYSTEM TEST", "[TEST ONLY]", "NO CUSTOMER", "SYNTHETIC DEMO")
CONSENT = (
    "- [x] I understand this issue is public and contains no secrets, personal data, payment details, or confidential material.",
    "- [x] I understand any price, delivery and live system access require separate human agreement and explicit approval.",
)


class SourceRejected(ValueError):
    """A public record is ineligible for safe CRM drafting."""


def fetch_open_issues(*, opener=None, max_issues=30, token=None):
    """Fetch direct from GitHub over verified HTTPS; no user-controlled URLs."""
    if not isinstance(max_issues, int) or isinstance(max_issues, bool) or not 1 <= max_issues <= 100:
        raise SourceRejected("INVALID_LIMIT")
    opener = opener or urllib.request.urlopen
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "imperial-core-commercial-readonly-discovery",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(GITHUB_API + "/issues?state=open&per_page=" + str(max_issues), headers=headers)
    with opener(req, timeout=15) as response:
        raw = response.read(MAX_RESPONSE + 1)
    if len(raw) > MAX_RESPONSE:
        raise SourceRejected("RESPONSE_TOO_LARGE")
    try:
        issues = json.loads(raw)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise SourceRejected("INVALID_API_JSON") from exc
    if not isinstance(issues, list) or len(issues) > max_issues:
        raise SourceRejected("INVALID_API_COLLECTION")
    return issues


def sanitized_candidate(raw):
    """Validate GitHub API record and independently re-triage public content.

    MUST be called only on records fetched by fetch_open_issues, not user JSON.
    Returns no title, body, login, contact information or other personal data.
    """
    if not isinstance(raw, dict) or raw.get("pull_request") is not None:
        raise SourceRejected("NON_ISSUE")
    number = raw.get("number")
    if not isinstance(number, int) or isinstance(number, bool) or not 1 <= number <= 9999999999999:
        raise SourceRejected("INVALID_NUMBER")
    if raw.get("url") != GITHUB_API + "/issues/" + str(number):
        raise SourceRejected("UNTRUSTED_REPOSITORY")
    if raw.get("html_url") != "https://github.com/" + REPO + "/issues/" + str(number):
        raise SourceRejected("UNTRUSTED_PUBLIC_LINK")
    if raw.get("state") != "open":
        raise SourceRejected("NOT_OPEN")
    user = raw.get("user")
    if (not isinstance(user, dict) or not isinstance(user.get("login"), str)
            or not user["login"] or user.get("type") != "User"):
        raise SourceRejected("MISSING_AUTHOR")
    if user["login"].casefold() == OWNER.casefold():
        raise SourceRejected("OWNER_TEST_NOT_CUSTOMER")
    labels = raw.get("labels")
    if not isinstance(labels, list):
        raise SourceRejected("LABELS_REQUIRED")
    if any(isinstance(label, dict) and isinstance(label.get("name"), str)
           and re.search(r"privacy-review-required|commercial-scope-review|test|spam", label["name"], re.I)
           for label in labels):
        raise SourceRejected("SOURCE_ON_HOLD")
    title, body = raw.get("title"), raw.get("body")
    if not isinstance(title, str) or not isinstance(body, str):
        raise SourceRejected("MISSING_PUBLIC_SCOPE")
    if len(title) > 250 or len(body) > 8000:
        raise SourceRejected("OUT_OF_BOUNDS")
    if any(marker in (title + "\n" + body).upper() for marker in TEST_MARKERS):
        raise SourceRejected("SYNTHETIC_NOT_CUSTOMER")
    if EMAIL.search(title + "\n" + body):
        raise SourceRejected("PUBLIC_PRIVACY_REVIEW_REQUIRED")
    if not all(text in body for text in CONSENT):
        raise SourceRejected("UNCONFIRMED_CONSENT")
    if triage({"issue": raw})["decision"] != "PUBLIC_ENQUIRY_RECEIVED":
        raise SourceRejected("TRIAGE_NOT_APPROVED")
    candidate = {
        "number": number,
        "repository": REPO,
        "decision": "PUBLIC_ENQUIRY_RECEIVED",
        "author": user["login"],
        "state": "open",
        "test": False,
    }
    source_number, digest = receipt(candidate)
    return {
        "workspace_id": WORKSPACE,
        "demand_source": SOURCE,
        "source_ref": "github:" + REPO + "#" + source_number,
        "source_receipt_hash": digest,
        "need": "IC-OFFER-001: automation failure audit; pending human scope/privacy review",
        "state": "LEAD_CREATED",
    }


def discover(issues):
    """Produce reviewable non-binding draft references; never return raw content."""
    result = []
    rejected = 0
    if not isinstance(issues, list):
        raise SourceRejected("INVALID_COLLECTION")
    for raw in issues:
        try:
            result.append(sanitized_candidate(raw))
        except SourceRejected:
            rejected += 1
        except ValueError:
            rejected += 1
    return {
        "mode": "READ_ONLY_DRAFT_DISCOVERY",
        "offer_id": "IC-OFFER-001",
        "drafts": result,
        "eligible_count": len(result),
        "rejected_or_ignored_count": rejected,
        "dispatch_allowed": False,
        "owner_review_required": True,
        "payments_verified": 0,
    }


def main():
    parser = argparse.ArgumentParser(description="Read-only public commercial issue discovery")
    parser.add_argument("--max-issues", type=int, default=30)
    parser.add_argument("--output", type=Path, help="Write sanitized, non-binding draft manifest")
    args = parser.parse_args()
    result = discover(fetch_open_issues(max_issues=args.max_issues))
    if args.output:
        if args.output.exists() or args.output.is_symlink():
            raise SourceRejected("OUTPUT_EXISTS_NO_OVERWRITE")
        args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "mode": result["mode"],
        "eligible_count": result["eligible_count"],
        "rejected_or_ignored_count": result["rejected_or_ignored_count"],
        "dispatch_allowed": False,
        "payments_verified": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
