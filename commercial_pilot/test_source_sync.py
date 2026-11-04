import json
import unittest
from urllib.parse import parse_qs, urlsplit

from commercial_pilot.source_sync import (
    GITHUB_API, REPO, CONSENT, SourceRejected,
    discover, sanitized_candidate, fetch_open_issues,
)

def good_issue():
    return {
        "number": 91,
        "url": GITHUB_API + "/issues/91",
        "html_url": "https://github.com/" + REPO + "/issues/91",
        "user": {"login": "external-client-example", "type": "User"},
        "labels": [],
        "state": "open",
        "title": "[Audit request] Intermittent webhook errors",
        "body": "\n".join([
            "### What should be assessed?",
            "One webhook or API integration",
            "### Public, non-confidential description of the problem",
            "We observe duplicates and HTTP 429.",
            "### Expected first deliverable",
            "Diagnostic report and reproducible synthetic test",
            "### Public issue privacy and scope confirmation",
            *CONSENT,
        ]),
    }


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, limit):
        return self.payload[:limit]


class SourceSyncTests(unittest.TestCase):
    def test_real_issue_becomes_only_sanitized_draft(self):
        draft = sanitized_candidate(good_issue())
        self.assertEqual(draft["state"], "LEAD_CREATED")
        self.assertEqual(draft["workspace_id"], "IMPERIAL-GLOBAL")
        self.assertEqual(len(draft["source_receipt_hash"]), 64)
        self.assertNotIn("external-client-example", json.dumps(draft))
        self.assertNotIn("webhook errors", json.dumps(draft))

    def test_owner_is_not_a_client(self):
        x = good_issue()
        x["user"]["login"] = "oromaskevic23-cmd"
        with self.assertRaises(SourceRejected):
            sanitized_candidate(x)

    def test_bot_and_review_hold_are_not_candidates(self):
        for edit in ("bot", "hold", "missing_labels"):
            x = good_issue()
            if edit == "bot":
                x["user"]["type"] = "Bot"
            elif edit == "hold":
                x["labels"] = [{"name": "privacy-review-required"}]
            else:
                del x["labels"]
            with self.assertRaises(SourceRejected):
                sanitized_candidate(x)

    def test_synthetic_is_not_a_client(self):
        x = good_issue()
        x["body"] += "\nSYSTEM TEST ONLY — NO CUSTOMER"
        with self.assertRaises(SourceRejected):
            sanitized_candidate(x)

    def test_missing_consent_denied(self):
        x = good_issue()
        x["body"] = x["body"].replace("- [x] I understand any price", "- [ ] I understand any price")
        with self.assertRaises(SourceRejected):
            sanitized_candidate(x)

    def test_incomplete_form_and_sensitive_title_are_not_candidates(self):
        for edit in ("empty", "invalid", "secret_title"):
            x = good_issue()
            if edit == "empty":
                x["body"] = x["body"].replace("We observe duplicates and HTTP 429.", "_No response_")
            elif edit == "invalid":
                x["body"] = x["body"].replace("One webhook or API integration", "")
            else:
                x["title"] += " sk-abcdefghijklmnopqrstuvwxyz123"
            with self.assertRaises(SourceRejected):
                sanitized_candidate(x)

    def test_secrets_and_pii_denied(self):
        for payload in ("contact me at owner@example.com", "Authorization: Bearer abcdefghijklmnopqrstuvwxyz123"):
            x = good_issue()
            x["body"] += "\n" + payload
            with self.assertRaises(SourceRejected):
                sanitized_candidate(x)

    def test_wrong_repository_denied(self):
        x = good_issue()
        x["url"] = "https://api.github.com/repos/evil/repo/issues/91"
        with self.assertRaises(SourceRejected):
            sanitized_candidate(x)

    def test_pr_and_closed_denied(self):
        x = good_issue()
        x["pull_request"] = {}
        with self.assertRaises(SourceRejected):
            sanitized_candidate(x)
        x = good_issue()
        x["state"] = "closed"
        with self.assertRaises(SourceRejected):
            sanitized_candidate(x)

    def test_boolean_issue_id_denied(self):
        x = good_issue()
        x["number"] = True
        with self.assertRaises(SourceRejected):
            sanitized_candidate(x)

    def test_discover_is_read_only_and_counts_ignored(self):
        result = discover([good_issue(), {"number": 2}])
        self.assertEqual(result["eligible_count"], 1)
        self.assertEqual(result["rejected_or_ignored_count"], 1)
        self.assertFalse(result["dispatch_allowed"])
        self.assertEqual(result["payments_verified"], 0)
        self.assertEqual(result["payment_status"], "NOT_CHECKED_NO_PROVIDER")

    def test_api_fetch_uses_bound_github_host(self):
        calls = []
        def opener(req, timeout):
            calls.append((req.full_url, timeout))
            page = int(parse_qs(urlsplit(req.full_url).query)["page"][0])
            return FakeResponse(json.dumps([good_issue()] if page == 1 else []).encode())
        records = fetch_open_issues(opener=opener, max_issues=1)
        self.assertEqual(len(records), 1)
        self.assertEqual(calls, [(GITHUB_API + "/issues?state=open&per_page=1&page=1", 15),
                                 (GITHUB_API + "/issues?state=open&per_page=1&page=2", 15)])

    def test_discovers_candidate_on_second_page(self):
        issue = good_issue()
        ignored = [{"number": n} for n in range(1, 101)]
        issue["number"] = 101
        issue["url"] = GITHUB_API + "/issues/101"
        issue["html_url"] = "https://github.com/" + REPO + "/issues/101"
        calls = []
        def opener(req, timeout):
            query = parse_qs(urlsplit(req.full_url).query)
            calls.append(query)
            page = int(query["page"][0])
            return FakeResponse(json.dumps(ignored if page == 1 else [issue]).encode())
        issues = fetch_open_issues(opener=opener, max_issues=300)
        self.assertEqual(len(issues), 101)
        self.assertEqual(discover(issues)["eligible_count"], 1)
        self.assertEqual([q["page"][0] for q in calls], ["1", "2"])

    def test_exceeding_scan_budget_is_explicit_failure(self):
        def opener(req, timeout):
            page = int(parse_qs(urlsplit(req.full_url).query)["page"][0])
            return FakeResponse(json.dumps([{"number": page}]).encode())
        with self.assertRaisesRegex(SourceRejected, "SCAN_LIMIT_EXCEEDED"):
            fetch_open_issues(opener=opener, max_issues=1)

    def test_duplicate_across_pages_fails_instead_of_double_counting(self):
        def opener(req, timeout):
            page = int(parse_qs(urlsplit(req.full_url).query)["page"][0])
            return FakeResponse(json.dumps([{"number": 1}, {"number": 2}] if page == 1 else [{"number": 1}]).encode())
        with self.assertRaisesRegex(SourceRejected, "SCAN_UNSTABLE_DUPLICATE"):
            fetch_open_issues(opener=opener, max_issues=2)

    def test_limit_is_fail_closed(self):
        for n in (0, 1001, True, "10"):
            with self.assertRaises(SourceRejected):
                fetch_open_issues(max_issues=n)

    def test_invalid_api_response_denied(self):
        with self.assertRaises(SourceRejected):
            fetch_open_issues(opener=lambda req, timeout: FakeResponse(b'{"message":"rate limited"}'))


if __name__ == "__main__":
    unittest.main()
