import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("annotation_agreement", Path(__file__).resolve().parents[1]/"scripts/annotation_agreement.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AgreementTests(unittest.TestCase):
    def test_empty_does_not_fabricate_agreement(self):
        result = module.agreement([], "a", "b")
        self.assertIsNone(result["cohen_kappa"])
        self.assertEqual(result["paired_records"], 0)

    def test_unknown_stays_distinct_and_unpaired_excluded(self):
        rows = [{"record_id": "fixture1", "annotator_id": "a", "topic_ai": "yes"},
                {"record_id": "fixture1", "annotator_id": "b", "topic_ai": "uncertain"},
                {"record_id": "fixture2", "annotator_id": "a", "topic_ai": "no"}]
        result = module.agreement(rows, "a", "b")
        self.assertEqual(result["observed_agreement"], 0)
        self.assertEqual(result["unpaired_records"], 1)

    def test_duplicate_annotation_fails(self):
        rows = [{"record_id": "fixture1", "annotator_id": "a", "topic_ai": "yes"}]*2
        with self.assertRaises(ValueError):
            module.agreement(rows, "a", "b")

    def test_unvarying_labels_report_degenerate_kappa(self):
        rows = [{"record_id": "fixture1", "annotator_id": who, "topic_ai": "yes"} for who in ["a", "b"]]
        result = module.agreement(rows, "a", "b")
        self.assertEqual(result["observed_agreement"], 1)
        self.assertIsNone(result["cohen_kappa"])


if __name__ == "__main__":
    unittest.main()
