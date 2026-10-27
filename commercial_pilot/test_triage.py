import unittest
from triage import triage

def event(title="[Audit request] Workflow problem", body=None):
    if body is None:
        body = "\n".join([
            "### What should be assessed?",
            "One webhook or API integration",
            "### Public, non-confidential description of the problem",
            "Duplicate events with backoff.",
            "### Expected first deliverable",
            "Audit report",
            "### Public issue privacy and scope confirmation",
            "- [x] I understand this issue is public.",
        ])
    return {"issue": {"title": title, "body": body}}

class IntakeTests(unittest.TestCase):
    def test_valid_enquiry_only(self):
        self.assertEqual(triage(event()), {"decision": "PUBLIC_ENQUIRY_RECEIVED", "reply_allowed": True})
    def test_other_issue_ignored(self):
        self.assertEqual(triage(event(title="Unrelated"))["decision"], "IGNORE")
    def test_no_scope_cannot_be_auto_approved(self):
        self.assertEqual(triage(event(body="Please help"))["decision"], "SCOPE_REVIEW_REQUIRED")
    def test_private_key_never_auto_replied(self):
        body = event()["issue"]["body"] + "\n-----BEGIN PRIVATE KEY-----"
        self.assertEqual(triage(event(body=body)), {"decision": "PRIVACY_REVIEW_REQUIRED", "reply_allowed": False})
    def test_token_never_auto_replied(self):
        body = event()["issue"]["body"] + "\nAuthorization: Bearer abcdefghijklmnopqrstuvwxyz123"
        self.assertEqual(triage(event(body=body))["decision"], "PRIVACY_REVIEW_REQUIRED")
    def test_long_body_quarantined(self):
        self.assertEqual(triage(event(body="a" * 8001))["decision"], "PRIVACY_REVIEW_REQUIRED")
    def test_pr_ignored(self):
        e = event()
        e["issue"]["pull_request"] = {"url": "https://example.test"}
        self.assertEqual(triage(e)["decision"], "IGNORE")
if __name__ == "__main__":
    unittest.main()
