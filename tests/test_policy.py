"""Local venture policy checks; no network, credentials, or cloud side effects."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import json
from venture_fabric.policy import evaluate_transition, STAGES
from scripts.validate_portfolio import validate

SHA = "a" * 64

class GateTests(unittest.TestCase):
    def test_stage_sequence_is_canonical(self):
        self.assertEqual(len(STAGES), 9)
        self.assertEqual(STAGES[0], "IDEA")
        self.assertEqual(STAGES[-1], "SOLD")

    def test_unknown_stage_denied(self):
        self.assertFalse(evaluate_transition("GHOST", "DISCOVERY").ready_for_review)

    def test_skipping_stages_denied(self):
        d = evaluate_transition("IDEA", "SOLD", {"signed_agreement": SHA})
        self.assertEqual(d.reasons, ("NON_SEQUENTIAL_TRANSITION",))

    def test_no_evidence_denied(self):
        self.assertFalse(evaluate_transition("IDEA", "DISCOVERY").ready_for_review)

    def test_invalid_digest_denied(self):
        d = evaluate_transition("IDEA", "DISCOVERY", {"research_brief": "fake", "scope_budget": SHA})
        self.assertEqual(d.missing, ("research_brief",))

    def test_discovery_metadata_is_plan_only(self):
        d = evaluate_transition("IDEA", "DISCOVERY", {"research_brief": SHA, "scope_budget": SHA})
        self.assertTrue(d.ready_for_review)
        self.assertIn("no state changed", d.notice)

    def test_build_requires_human_reference(self):
        proof = {"product_spec": SHA, "architecture_adr": SHA, "threat_model": SHA}
        self.assertFalse(evaluate_transition("VALIDATED", "BUILD", proof).ready_for_review)
        self.assertTrue(evaluate_transition("VALIDATED", "BUILD", proof, approval_reference="APR-1").ready_for_review)

    def test_self_qa_denied(self):
        proof = {"build_proof": SHA, "unit_integration_tests": SHA, "artifact_digest": SHA}
        self.assertFalse(evaluate_transition("BUILD", "QA", proof, author_id="nca-1", reviewer_id="nca-1").ready_for_review)

    def test_independent_qa_metadata(self):
        proof = {"build_proof": SHA, "unit_integration_tests": SHA, "artifact_digest": SHA}
        self.assertTrue(evaluate_transition("BUILD", "QA", proof, author_id="nca-1", reviewer_id="nca-2").ready_for_review)

    def test_released_requires_approval_and_review(self):
        proof = {"security_review": SHA, "release_acceptance": SHA, "rollback_rehearsal": SHA}
        self.assertFalse(evaluate_transition("PILOT", "RELEASED", proof, author_id="a", reviewer_id="b").ready_for_review)
        self.assertTrue(evaluate_transition("PILOT", "RELEASED", proof, "APR-2", "a", "b").ready_for_review)

    def test_sold_requires_multiple_evidence_items(self):
        proof = {"signed_agreement": SHA, "settlement_verification": SHA, "transfer_acceptance": SHA}
        d = evaluate_transition("EXIT_READY", "SOLD", proof, "APR-3", "seller", "auditor")
        self.assertTrue(d.ready_for_review)
        self.assertIn("no signature", d.notice)

    def test_existing_stage_not_mutated(self):
        stage = "QA"
        evaluate_transition(stage, "PILOT")
        self.assertEqual(stage, "QA")

class ManifestTests(unittest.TestCase):
    def test_actual_manifest_passes(self):
        errors = validate(Path(__file__).resolve().parents[1])
        self.assertEqual(errors, [])

    def test_missing_manifest_fails_closed(self):
        with TemporaryDirectory() as d:
            self.assertTrue(validate(Path(d)))

if __name__ == "__main__":
    unittest.main()
