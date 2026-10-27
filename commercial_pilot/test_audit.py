import json
import tempfile
import unittest
from pathlib import Path

from audit import IntakeRejected, load_packet, run
from verify import crosscheck


class CommercialPilotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.src = self.root / "input.json"
        self.payload = {
            "workflow": "CLIENT_DEMO",
            "events": [
                {"id": "evt1", "status": 200, "duration_ms": 40},
                {"id": "evt1", "status": 429, "duration_ms": 55},
                {"id": "evt2", "status": 503, "duration_ms": 30002},
                {"id": "evt3", "status": "timeout", "duration_ms": 60000},
            ],
        }
        self.write()

    def write(self):
        self.src.write_text(json.dumps(self.payload), encoding="utf-8")

    def test_actual_lab_report_and_second_path_qa(self):
        report = run(self.src, self.root / "out")
        self.assertEqual(report["findings"]["duplicate_event_ids"], 1)
        self.assertEqual(report["findings"]["http_429"], 1)
        self.assertEqual(report["findings"]["http_5xx"], 1)
        self.assertEqual(report["findings"]["timeouts"], 1)
        self.assertEqual(report["findings"]["slow_over_30s"], 2)
        receipt = crosscheck(self.src, self.root / "out/report.json", self.root / "out/qa_receipt.json")
        self.assertEqual(receipt["result"], "AUTOMATED_CROSSCHECK_PASS_NOT_HUMAN_QA")
        self.assertFalse(receipt["payment_confirmed"])
        self.assertEqual(report["collected_revenue_usd"], 0)

    def test_no_duplicate_write(self):
        run(self.src, self.root / "out")
        with self.assertRaisesRegex(IntakeRejected, "OUTPUT_EXISTS"):
            run(self.src, self.root / "out")

    def test_no_secrets_or_extra_fields(self):
        self.payload["events"][0]["api_key"] = "unsafe"
        self.write()
        with self.assertRaisesRegex(IntakeRejected, "UNEXPECTED_EVENT_FIELDS"):
            load_packet(self.src)

    def test_no_pii_in_workflow_name(self):
        self.payload["workflow"] = "someone@example.com"
        self.write()
        with self.assertRaisesRegex(IntakeRejected, "INVALID_WORKFLOW_ID"):
            load_packet(self.src)

    def test_no_bool_as_status(self):
        self.payload["events"][0]["status"] = True
        self.write()
        with self.assertRaisesRegex(IntakeRejected, "INVALID_EVENT_STATUS"):
            load_packet(self.src)

    def test_tamper_denied(self):
        run(self.src, self.root / "out")
        output = self.root / "out/report.json"
        report = json.loads(output.read_text())
        report["findings"]["http_429"] = 0
        output.write_text(json.dumps(report))
        with self.assertRaisesRegex(ValueError, "EVIDENCE_MISMATCH"):
            crosscheck(self.src, output, self.root / "out/qa_receipt.json")

    def test_oversize_denied(self):
        self.src.write_bytes(b"0" * (256 * 1024 + 1))
        with self.assertRaisesRegex(IntakeRejected, "INPUT_FILE_REJECTED"):
            load_packet(self.src)

    def test_symlink_denied(self):
        alias = self.root / "link.json"
        alias.symlink_to(self.src)
        with self.assertRaisesRegex(IntakeRejected, "INPUT_FILE_REJECTED"):
            load_packet(alias)


if __name__ == "__main__":
    unittest.main()
