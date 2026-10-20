"""Synthetic fixtures only: integrity, page boundaries and private diagnostics."""
from __future__ import annotations

import contextlib
import io
import json
import logging
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from synesis.corpus import (build_corpus, chunk_text, extract_pdf, hash_file,
                            hash_text, normalize_page_text, search_corpus)


def fixture_record(key="fixture-a", institution="fixture"):
    return {"id": key, "institution_id": institution, "title": "Synthetic software fixture",
            "year": 2024, "degree_level": "master", "language": "en",
            "source_url": "https://example.invalid/synthetic", "abstract": None,
            "academic_date_verified": False}


def jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def extracted(*texts):
    pages = [{"page_number": i, "text": text, "status": "text_extracted" if text.strip() else "ocr_needed",
              "error_code": None, "text_sha256": hash_text(text)} for i, text in enumerate(texts, 1)]
    present = sum(bool(text.strip()) for text in texts)
    return {"status": "text_extracted" if present == len(texts) else "partial_text" if present else "ocr_needed",
            "error_code": None, "pages": pages, "warning_count": 0}


class CorpusFixtures(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        jsonl(self.root / "data/research_225/spain.jsonl", [fixture_record()])
        jsonl(self.root / "data/research_225/global.jsonl", [])

    def pdf_entry(self, name="fixture.pdf", value=b"%PDF-SYNTHETIC-FIXTURE-ONLY\n"):
        path = self.root / "data/fulltext/pdf/fixture" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value)
        return {"path": path.relative_to(self.root).as_posix(), "sha256": hash_file(path),
                "bytes": len(value), "download_url": "https://example.invalid/synthetic.pdf",
                "source_license": "fixture-license-not-a-research-license"}

    def sources(self, rows):
        jsonl(self.root / "data/fulltext/sources_spain.jsonl", rows)

    def read(self, name):
        return [json.loads(line) for line in (self.root / "data/derived" / name).read_text().splitlines()]

    def test_metadata_catalog_survives_missing_manifests_without_adding_pilot(self):
        jsonl(self.root / "data/pilot/rights_cleared.jsonl", [fixture_record("do-not-add")])
        summary = build_corpus(self.root)
        self.assertEqual(summary["metadata_records"], 1)
        self.assertEqual(summary["pilot_records_added"], 0)
        self.assertEqual(self.read("catalog.jsonl")[0]["fulltext_status"], "not_downloaded")
        self.assertEqual(summary["document_count"], 0)

    def test_checksum_is_checked_before_extraction_and_other_work_survives(self):
        jsonl(self.root / "data/research_225/spain.jsonl", [fixture_record(), fixture_record("fixture-b")])
        bad = self.pdf_entry("bad.pdf", b"same-sized-initial-payload")
        (self.root / bad["path"]).write_bytes(b"same-sized-altered-payload")
        good = self.pdf_entry("good.pdf")
        self.sources([{"record_id": "fixture-a", "status": "downloaded", "files": [bad]},
                      {"record_id": "fixture-b", "status": "downloaded", "files": [good]}])
        called = []
        def reader(path):
            called.append(path.name)
            return extracted("A searchable synthetic page")
        summary = build_corpus(self.root, extractor=reader)
        self.assertEqual(called, ["good.pdf"])
        self.assertEqual(summary["issue_counts"].get("checksum_mismatch"), 1)
        self.assertEqual(summary["records_with_text"], 1)
        self.assertEqual(self.read("documents.jsonl")[0]["status"], "checksum_mismatch")

    def test_chunks_keep_unicode_offsets_page_work_and_rights_provenance(self):
        entry = self.pdf_entry()
        self.sources([{"record_id": "fixture-a", "status": "downloaded", "files": [entry]}])
        pages = ("café 🌍 one two three\nfour\u2028five\u0085six seven " * 3, "Distinct second page.")
        build_corpus(self.root, extractor=lambda _: extracted(*pages), max_chars=40, overlap=8)
        by_id = {row["page_id"]: row for row in self.read("pages.jsonl")}
        chunks = self.read("chunks.jsonl")
        self.assertGreater(len(chunks), 2)
        for chunk in chunks:
            page = by_id[chunk["page_id"]]
            self.assertEqual(chunk["text"], page["text"][chunk["start_char"]:chunk["end_char"]])
            self.assertLessEqual(len(chunk["text"]), 40)
            self.assertEqual(chunk["text_sha256"], hash_text(chunk["text"]))
            self.assertEqual(chunk["record_id"], page["record_id"])
            self.assertEqual(chunk["page_number"], page["page_number"])
            self.assertEqual(chunk["pdf_sha256"], entry["sha256"])
            self.assertEqual(chunk["source_license"], entry["source_license"])
        self.assertEqual(hash_file(self.root / entry["path"]), entry["sha256"])

    def test_same_pdf_is_cached_but_work_and_page_groups_never_mix(self):
        jsonl(self.root / "data/research_225/spain.jsonl", [fixture_record(), fixture_record("fixture-b", "other")])
        entry = self.pdf_entry()
        self.sources([{"record_id": "fixture-a", "files": [entry, entry]},
                      {"record_id": "fixture-b", "files": [entry]}])
        calls = []
        def reader(path):
            calls.append(path)
            return extracted("Shared bytes, separate works.")
        summary = build_corpus(self.root, extractor=reader)
        self.assertEqual(len(calls), 1)
        self.assertEqual(summary["document_count"], 2)
        self.assertEqual(summary["cache_hits"], 1)
        self.assertEqual(len({row["document_id"] for row in self.read("documents.jsonl")}), 2)
        self.assertEqual({row["work_group_id"] for row in self.read("chunks.jsonl")}, {"fixture-a", "fixture-b"})
        with contextlib.closing(sqlite3.connect(self.root / "data/derived/corpus.sqlite")) as db:
            self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])
            self.assertEqual(db.execute("SELECT count(*) FROM metadata").fetchone()[0], 2)
        original_chunks = (self.root / "data/derived/chunks.jsonl").read_bytes()
        again = build_corpus(self.root, extractor=reader)
        self.assertEqual(again["cache_hits"], 2)
        self.assertEqual(len(calls), 1)
        self.assertEqual((self.root / "data/derived/chunks.jsonl").read_bytes(), original_chunks)

    def test_corrupt_cache_is_rebuilt_and_no_cross_document_chunks_appear(self):
        entry = self.pdf_entry()
        self.sources([{"record_id": "fixture-a", "files": [entry]}])
        calls = []
        def reader(_):
            calls.append(1)
            return extracted("Known original synthetic page")
        build_corpus(self.root, extractor=reader)
        cache = next((self.root / "data/derived/.cache").glob("*.json"))
        value = json.loads(cache.read_text())
        value["result"]["pages"][0]["text"] = "altered cache text"
        cache.write_text(json.dumps(value))
        build_corpus(self.root, extractor=reader)
        self.assertEqual(len(calls), 2)
        self.assertEqual(self.read("pages.jsonl")[0]["text"], "Known original synthetic page")

    def test_source_paths_cannot_escape_repository_including_symlinks(self):
        entry = self.pdf_entry()
        with tempfile.TemporaryDirectory() as other:
            outside = Path(other) / "outside.pdf"
            outside.write_bytes(b"synthetic outside root")
            link = self.root / "escape.pdf"
            link.symlink_to(outside)
            entry.update(path="escape.pdf", sha256=hash_file(outside), bytes=outside.stat().st_size)
            self.sources([{"record_id": "fixture-a", "files": [entry]}])
            summary = build_corpus(self.root, extractor=lambda _: self.fail("escaped file opened"))
        self.assertEqual(summary["issue_counts"], {"unsafe_path": 1})
        self.assertEqual(summary["page_count"], 0)

    def test_parser_exceptions_do_not_leak_contacts_or_page_text_into_diagnostics(self):
        entry = self.pdf_entry()
        self.sources([{"record_id": "fixture-a", "files": [entry]}])
        secret = "sensitive-fixture@example.invalid"
        def reader(_):
            raise ValueError("Page contact " + secret)
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            summary = build_corpus(self.root, extractor=reader)
        self.assertNotIn(secret, output.getvalue())
        self.assertNotIn(secret, json.dumps(summary))
        self.assertNotIn(secret, (self.root / "data/derived/documents.jsonl").read_text())
        self.assertEqual(self.read("documents.jsonl")[0]["error_code"], "pdf_parse_failed")

    def test_ocr_status_keeps_empty_pages_without_inventing_text(self):
        entry = self.pdf_entry()
        self.sources([{"record_id": "fixture-a", "files": [entry]}])
        summary = build_corpus(self.root, extractor=lambda _: extracted("", "  "))
        self.assertEqual(summary["page_status_counts"], {"ocr_needed": 2})
        self.assertEqual(summary["chunk_count"], 0)
        self.assertEqual(self.read("catalog.jsonl")[0]["fulltext_status"], "ocr_needed")

    def test_fts_search_returns_citations_and_filters_without_mutating_database(self):
        jsonl(self.root / "data/research_225/spain.jsonl", [fixture_record(), fixture_record("fixture-b", "other")])
        one, two = self.pdf_entry("one.pdf", b"one-fixture"), self.pdf_entry("two.pdf", b"two-fixture")
        self.sources([{"record_id": "fixture-a", "files": [one]}, {"record_id": "fixture-b", "files": [two]}])
        build_corpus(self.root, extractor=lambda _: extracted("Métodos de investigación reproducible"))
        database = self.root / "data/derived/corpus.sqlite"
        before = hash_file(database)
        results = search_corpus(database, "investigacion", institution="fixture", limit=1)
        if results["engine"] != "fts5":
            results = search_corpus(database, "investigación", institution="fixture", limit=1)
        self.assertEqual(len(results["results"]), 1)
        hit = results["results"][0]
        self.assertEqual(hit["record_id"], "fixture-a")
        self.assertEqual(hit["page_number"], 1)
        self.assertEqual(hit["pdf_path"], one["path"])
        self.assertEqual(hash_file(database), before)
        self.assertEqual(search_corpus(database, "none", year_min=2030)["results"], [])
        if results["engine"] == "fts5":
            with self.assertRaisesRegex(ValueError, "invalid_search_query"):
                search_corpus(database, '"unterminated')
            with contextlib.closing(sqlite3.connect(database)) as db:
                db.execute("DROP TABLE chunks_fts")
                db.commit()
        fallback = search_corpus(database, "investigación")
        self.assertEqual(fallback["engine"], "literal_like_fallback")
        self.assertEqual(len(fallback["results"]), 2)
        self.assertEqual(search_corpus(database, "%")["results"], [])

    def test_invalid_manifest_is_isolated_and_duplicate_metadata_is_fatal(self):
        path = self.root / "data/fulltext/sources_spain.jsonl"
        path.parent.mkdir(parents=True)
        path.write_text("not-json-sensitive-fixture@example.invalid")
        summary = build_corpus(self.root)
        self.assertEqual(summary["issue_counts"], {"invalid_source_manifest": 1})
        self.assertEqual(summary["metadata_records"], 1)
        jsonl(self.root / "data/research_225/global.jsonl", [fixture_record()])
        with self.assertRaisesRegex(ValueError, "duplicate_metadata_id"):
            build_corpus(self.root)


class ExtractionUnitChecks(unittest.TestCase):
    def test_chunk_configuration_and_normalization(self):
        self.assertEqual(normalize_page_text("cafe\u0301\r\nword\x00"), "café\nword")
        self.assertEqual(chunk_text(""), [])
        for length, overlap in [(0, 0), (5, 5), (5, -1)]:
            with self.assertRaisesRegex(ValueError, "invalid_chunk_configuration"):
                chunk_text("content", length, overlap)

    def test_pdf_reader_keeps_ocr_and_page_error_statuses_and_suppresses_parser_logs(self):
        try:
            import pypdf
        except ImportError:
            self.skipTest("Optional PDF dependency is not installed")
        class Page:
            def __init__(self, text):
                self.text = text
            def extract_text(self):
                if self.text is None:
                    raise ValueError("sensitive-fixture@example.invalid")
                return self.text
        class Reader:
            is_encrypted = False
            pages = [Page("cafe\u0301\r\nSynthetic page"), Page(""), Page(None)]
        logs = io.StringIO()
        handler = logging.StreamHandler(logs)
        parent = logging.getLogger()
        parent.addHandler(handler)
        self.addCleanup(parent.removeHandler, handler)
        def reader(*_args, **_kwargs):
            logging.getLogger("pypdf._reader").warning("sensitive-fixture@example.invalid")
            return Reader()
        with patch.object(pypdf, "PdfReader", side_effect=reader):
            result = extract_pdf(Path("unused-synthetic.pdf"))
        self.assertEqual(result["status"], "partial_text")
        self.assertEqual([p["status"] for p in result["pages"]], ["text_extracted", "ocr_needed", "page_error"])
        self.assertEqual(result["pages"][0]["text"], "café\nSynthetic page")
        self.assertNotIn("sensitive-fixture", logs.getvalue())


if __name__ == "__main__":
    unittest.main()
