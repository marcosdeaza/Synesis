import json
from pathlib import Path
import tempfile
import unittest

from synesis.fulltext import validate_fulltext


class FulltextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for folder in ("data/research_225", "data/fulltext"):
            (self.root / folder).mkdir(parents=True)
        self.metadata = {"id": "uev-example", "institution_id": "uev", "source_url": "https://example.org/work"}
        (self.root / "data/research_225/spain.jsonl").write_text(json.dumps(self.metadata) + "\n")
        (self.root / "data/research_225/global.jsonl").write_text("")
        self.source = {"record_id": "uev-example", "institution_id": "uev", "source_url": self.metadata["source_url"],
                       "status": "restricted", "files": []}
        (self.root / "data/fulltext/sources_global.jsonl").write_text("")
        self.save()

    def save(self):
        (self.root / "data/fulltext/sources_spain.jsonl").write_text(json.dumps(self.source) + "\n")

    def test_restricted_records_still_count_in_denominator(self):
        result = validate_fulltext(self.root)
        self.assertEqual(result["metadata_records"], 1)
        self.assertEqual(result["downloaded_records"], 0)
        self.assertEqual(result["statuses"], {"restricted": 1})
        self.assertEqual(result["unavailable"][0]["record_id"], "uev-example")

    def test_success_requires_evidence_of_file(self):
        self.source["status"] = "downloaded"
        self.save()
        with self.assertRaisesRegex(ValueError, "file_mismatch"):
            validate_fulltext(self.root)

    def test_path_traversal_rejected_before_file_access(self):
        self.source["status"] = "downloaded"
        self.source["files"] = [{"path": "data/fulltext/pdf/uev/uev-example/../../../../secret.pdf"}]
        self.save()
        with self.assertRaisesRegex(ValueError, "unsafe"):
            validate_fulltext(self.root)

    def test_missing_attempt_is_failure_unless_explicit_progress_mode(self):
        (self.root / "data/fulltext/sources_spain.jsonl").write_text("")
        with self.assertRaisesRegex(ValueError, "unattempted"):
            validate_fulltext(self.root)
        result = validate_fulltext(self.root, require_complete=False)
        self.assertEqual(result["unattempted_record_ids"], ["uev-example"])
