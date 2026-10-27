import unittest
from federated_bridge import intake, receipt, astra_handoff_candidate

GOOD = {"number": 32, "repository": "oromaskevic23-cmd/IMPERIAL-Venture-Factory",
        "decision": "PUBLIC_ENQUIRY_RECEIVED", "author": "outside-customer",
        "state": "open"}

class Cursor:
    def __init__(self, db):
        self.db = db
        self.result = None
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def execute(self, sql, params):
        assert "crm_sofft.lead_registry" in sql
        assert "ON CONFLICT (workspace_id,demand_source,source_receipt_hash) DO NOTHING" in sql
        key = params["source_ref"]
        self.result = None if key in self.db.keys else ("synthetic-id",)
        self.db.keys.add(key)
    def fetchone(self):
        return self.result

class FakeDB:
    def __init__(self):
        self.keys = set()
        self.commits = 0
    def cursor(self):
        return Cursor(self)
    def commit(self):
        self.commits += 1

class BridgeTests(unittest.TestCase):
    def test_dry_run_no_write(self):
        db = FakeDB()
        result = intake(db, GOOD)
        self.assertEqual(result["status"], "DRY_RUN")
        self.assertEqual(db.commits, 0)
        self.assertEqual(result["draft"]["workspace_id"], "IMPERIAL-GLOBAL")
    def test_idempotent_draft(self):
        db = FakeDB()
        self.assertEqual(intake(db, GOOD, dry_run=False)["status"], "DRAFT_INSERTED")
        self.assertEqual(intake(db, GOOD, dry_run=False)["status"], "DUPLICATE_IGNORED")
    def test_no_owner_synthetic(self):
        with self.assertRaises(ValueError):
            intake(FakeDB(), {**GOOD, "author": "oromaskevic23-cmd"})
    def test_no_test(self):
        with self.assertRaises(ValueError):
            receipt({**GOOD, "test": True})
    def test_no_untrusted_source(self):
        with self.assertRaises(ValueError):
            receipt({**GOOD, "repository": "attacker/another"})
    def test_no_untriaged_issue(self):
        with self.assertRaises(ValueError):
            receipt({**GOOD, "decision": "SCOPE_REVIEW_REQUIRED"})
    def test_no_closed_issue(self):
        with self.assertRaises(ValueError):
            receipt({**GOOD, "state": "closed"})
    def test_no_untrusted_body_persisted(self):
        db = FakeDB()
        payload = {**GOOD, "body": "PRIVATE_UNTRUSTED_TEXT"}
        result = intake(db, payload)
        self.assertNotIn("PRIVATE_UNTRUSTED_TEXT", str(result))
    def test_no_automatic_agent_execution(self):
        envelope = astra_handoff_candidate(GOOD)
        self.assertFalse(envelope["dispatch_allowed"])
        self.assertEqual(envelope["approval_gateway"], "NOT_APPROVED")
        self.assertEqual(envelope["audit_ledger"], "NOT_WRITTEN")

if __name__ == "__main__":
    unittest.main()
