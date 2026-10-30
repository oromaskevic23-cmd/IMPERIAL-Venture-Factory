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
            "Diagnostic report and reproducible synthetic test",
            "### Public issue privacy and scope confirmation",
            "- [x] I understand this issue is public and contains no secrets, personal data, payment details, or confidential material.",
            "- [x] I understand any price, delivery and live system access require separate human agreement and explicit approval.",
        ])
    return {"issue": {"title": title, "body": body}}

class IntakeTests(unittest.TestCase):
    def test_valid_enquiry_only(self):
        self.assertEqual(triage(event()), {"decision": "PUBLIC_ENQUIRY_RECEIVED", "reply_allowed": True})
    def test_other_issue_ignored(self):
        self.assertEqual(triage(event(title="Unrelated"))["decision"], "IGNORE")
    def test_no_scope_cannot_be_auto_approved(self):
        self.assertEqual(triage(event(body="Please help"))["decision"], "SCOPE_REVIEW_REQUIRED")
    def test_unchecked_consent_never_auto_acknowledged(self):
        body = event()["issue"]["body"].replace(
            "- [x] I understand any price", "- [ ] I understand any price")
        self.assertEqual(triage(event(body=body))["decision"], "SCOPE_REVIEW_REQUIRED")
    def test_private_key_never_auto_replied(self):
        body = event()["issue"]["body"] + "\n-----BEGIN PRIVATE KEY-----"
        self.assertEqual(triage(event(body=body)), {"decision": "PRIVACY_REVIEW_REQUIRED", "reply_allowed": False})
    def test_token_never_auto_replied(self):
        body = event()["issue"]["body"] + "\nAuthorization: Bearer abcdefghijklmnopqrstuvwxyz123"
        self.assertEqual(triage(event(body=body))["decision"], "PRIVACY_REVIEW_REQUIRED")
    def test_sensitive_title_and_email_are_never_acknowledged(self):
        for title in ("[Audit request] sk-abcdefghijklmnopqrstuvwxyz123", "[Audit request] person@example.com"):
            self.assertEqual(triage(event(title=title))["decision"], "PRIVACY_REVIEW_REQUIRED")
    def test_missing_answers_and_repeated_headings_are_not_complete(self):
        body = event()["issue"]["body"]
        for changed in (
            body.replace("Duplicate events with backoff.", "_No response_"),
            body.replace("One webhook or API integration", ""),
            body.replace("Diagnostic report and reproducible synthetic test", "Unexpected"),
            body + "\n### What should be assessed?\nOne webhook or API integration",
        ):
            self.assertEqual(triage(event(body=changed)), {"decision": "SCOPE_REVIEW_REQUIRED", "reply_allowed": False})
    def test_title_requires_a_specific_subject(self):
        self.assertEqual(triage(event(title="[Audit request] "))["decision"], "SCOPE_REVIEW_REQUIRED")
    def test_long_body_quarantined(self):
        self.assertEqual(triage(event(body="a" * 8001))["decision"], "PRIVACY_REVIEW_REQUIRED")
    def test_pr_ignored(self):
        e = event()
        e["issue"]["pull_request"] = {"url": "https://example.test"}
        self.assertEqual(triage(e)["decision"], "IGNORE")
if __name__ == "__main__":
    unittest.main()
