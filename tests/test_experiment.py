"""Synthetic software fixtures, separate from the real research corpus."""
import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "scripts/prepare_experiment.py"
SPEC = importlib.util.spec_from_file_location("synesis_prepare_experiment_test", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
make_assignments = MODULE.make_assignments


def metadata(count):
    return [{"id": f"fixture:{number}", "institution_id": "fixture"} for number in range(count)]


def source(number, *digests):
    return {"record_id": f"fixture:{number}", "files": [
        {"path": f"attachment_{i}.pdf", "sha256": digest} for i, digest in enumerate(digests)]}


class ExperimentSplits(unittest.TestCase):
    def test_shared_pdf_and_transitive_attachments_never_cross_partitions(self):
        rows = metadata(5)
        sources = [source(0, "a" * 64), source(1, "a" * 64, "b" * 64),
                   source(2, "b" * 64), source(3, "c" * 64)]
        result = make_assignments(rows, sources, 42)
        by_id = {row["record_id"]: row for row in result}
        group = [by_id[f"fixture:{i}"] for i in (0, 1, 2)]
        self.assertEqual(len({row["group_id"] for row in group}), 1)
        self.assertEqual(len({row["split"] for row in group}), 1)
        self.assertTrue(all(row["group_size"] == 3 and row["known_pdf_sha_count"] == 2 for row in group))
        self.assertNotEqual(by_id["fixture:3"]["group_id"], group[0]["group_id"])
        self.assertEqual(by_id["fixture:4"]["known_pdf_sha_count"], 0)

    def test_all_225_records_survive_including_ones_without_pdf(self):
        rows = metadata(225)
        result = make_assignments(rows, [source(0, "a" * 64), source(224, "a" * 64)], 42)
        self.assertEqual(len(result), 225)
        self.assertEqual({row["record_id"] for row in result}, {row["id"] for row in rows})
        self.assertTrue({row["split"] for row in result} <= {"train", "validation", "test"})

    def test_assignment_is_stable_under_input_order(self):
        rows = metadata(15)
        sources = [source(0, "d" * 64), source(4, "d" * 64), source(10, "e" * 64)]
        self.assertEqual(make_assignments(rows, sources, 123),
                         make_assignments(list(reversed(rows)), list(reversed(sources)), 123))

    def test_unknown_or_duplicate_metadata_cannot_be_silently_dropped(self):
        with self.assertRaises(ValueError):
            make_assignments(metadata(2) + metadata(1), [])
        with self.assertRaises(ValueError):
            make_assignments(metadata(2), [source(9, "a" * 64)])


if __name__ == "__main__":
    unittest.main()
