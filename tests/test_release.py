"""Release packaging and download security with synthetic fixtures and no network."""
from __future__ import annotations

import hashlib
import io
import json
import stat
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.download_release import (IntegrityError, download_asset, download_release,
                                     extract_archive, validate_archive)
from scripts.package_release import MANIFEST_NAME, SUMS_NAME, package_release
from synesis.corpus import build_corpus, hash_file, hash_text


def write_rows(path, values):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in values))


def fixture_extract(_):
    text = "Synthetic fixture research text only."
    return {"status": "text_extracted", "error_code": None,
            "pages": [{"page_number": 1, "text": text, "text_sha256": hash_text(text),
                       "status": "text_extracted", "error_code": None}]}


class Response(io.BytesIO):
    def __init__(self, data, status=200, headers=None):
        super().__init__(data)
        self.status = status
        self.headers = headers or {}

    def getcode(self):
        return self.status


class ReleaseFixtures(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "fixture-repo"
        self.root.mkdir()
        self.output = Path(self.temp.name) / "assets"
        records, sources = [], []
        for i in range(3):
            key = f"synthetic-fixture-{i}"
            row = {"id": key, "institution_id": "fixture", "title": "Synthetic fixture, not scientific data",
                   "source_url": f"https://example.invalid/fixture/{i}", "year": 2024,
                   "degree_level": "master", "abstract": None}
            records.append(row)
            files = []
            if i < 2:
                path = self.root / "data/fulltext/pdf/fixture" / f"fixture-{i}.pdf"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"%PDF-synthetic-test-fixture-not-a-real-document\n" + bytes([65 + i]) * 160)
                files.append({"path": path.relative_to(self.root).as_posix(), "bytes": path.stat().st_size,
                              "sha256": hash_file(path), "download_url": f"https://example.invalid/fixture/{i}.pdf",
                              "source_license": "synthetic-fixture-only"})
            sources.append({"record_id": key, "institution_id": "fixture", "source_url": row["source_url"],
                            "status": "downloaded" if files else "restricted", "files": files})
        write_rows(self.root / "data/research_225/spain.jsonl", records)
        write_rows(self.root / "data/research_225/global.jsonl", [])
        write_rows(self.root / "data/fulltext/sources_spain.jsonl", sources)
        write_rows(self.root / "data/fulltext/sources_global.jsonl", [])
        for name in ("data/research_225/PERMISSIONS.json", "data/fulltext/PERMISSIONS.json"):
            (self.root / name).write_text('{"fixture_only": true}\n')
        (self.root / "README.md").write_text("Synthetic fixture repository; not real research data.\n")
        build_corpus(self.root, extractor=fixture_extract)

    def package(self):
        return package_release(self.root, self.output, max_part_bytes=300)

    def fake_api(self, manifest):
        base = "https://github.com/marcosdeaza/Synesis/releases/download/v0.2.0"
        assets = []
        data = {}
        for name in [asset["name"] for asset in manifest["assets"]] + [MANIFEST_NAME, SUMS_NAME]:
            value = (self.output / name).read_bytes()
            url = f"{base}/{name}"
            data[url] = value
            assets.append({"name": name, "size": len(value), "browser_download_url": url,
                           "digest": "sha256:" + hashlib.sha256(value).hexdigest()})
        api = "https://api.github.com/repos/marcosdeaza/Synesis/releases/tags/v0.2.0"
        data[api] = json.dumps({"assets": assets}).encode()
        calls = []
        def opener(request, **_kwargs):
            calls.append(request.full_url)
            value = data[request.full_url]
            header = request.get_header("Range")
            if header:
                offset = int(header.removeprefix("bytes=").removesuffix("-"))
                return Response(value[offset:], 206, {"Content-Range": f"bytes {offset}-{len(value)-1}/{len(value)}"})
            return Response(value)
        return opener, calls, data

    def test_packages_split_pdfs_and_preserve_root_relative_paths_without_hash_cycle(self):
        (self.root / "data/derived/fixture.parquet").write_bytes(b"synthetic optional parquet fixture")
        manifest = self.package()
        self.assertEqual(manifest["metadata_records"], 3)
        self.assertEqual(manifest["pdf_files"], 2)
        parts = [a for a in manifest["assets"] if a["kind"] == "pdf"]
        self.assertEqual(len(parts), 2)
        self.assertTrue(all(a["parts"] == 2 and len(a["members"]) == 1 for a in parts))
        for asset in manifest["assets"]:
            self.assertEqual(hash_file(self.output / asset["name"]), asset["sha256"])
            with zipfile.ZipFile(self.output / asset["name"]) as archive:
                self.assertEqual(set(archive.namelist()), {m["path"] for m in asset["members"]})
                self.assertTrue(all(not n.startswith("/") and ".." not in Path(n).parts for n in archive.namelist()))
                for member in asset["members"]:
                    value = archive.read(member["path"])
                    self.assertEqual(len(value), member["bytes"])
                    self.assertEqual(hashlib.sha256(value).hexdigest(), member["sha256"])
        corpus = next(a for a in manifest["assets"] if a["kind"] == "corpus")
        self.assertIn("data/derived/fixture.parquet", [m["path"] for m in corpus["members"]])
        sums = {line.split("  ", 1)[1]: line.split("  ", 1)[0] for line in (self.output / SUMS_NAME).read_text().splitlines()}
        self.assertEqual(sums[MANIFEST_NAME], hash_file(self.output / MANIFEST_NAME))
        self.assertNotIn(SUMS_NAME, sums)
        self.assertNotIn(MANIFEST_NAME, {a["name"] for a in manifest["assets"]})

    def test_incomplete_ledger_and_stale_corpus_cannot_be_packaged(self):
        path = self.root / "data/fulltext/sources_spain.jsonl"
        original = path.read_text()
        path.write_text("\n".join(original.splitlines()[:-1]) + "\n")
        with self.assertRaisesRegex(ValueError, "unattempted_records"):
            self.package()
        self.assertFalse(self.output.exists())
        path.write_text(original + "\n")
        with self.assertRaisesRegex(ValueError, "corpus_inputs_changed"):
            self.package()
        self.assertFalse(self.output.exists())

    def test_default_download_fetches_metadata_and_corpus_then_optionally_pdfs(self):
        manifest = self.package()
        opener, calls, _ = self.fake_api(manifest)
        target = Path(self.temp.name) / "downloaded"
        first = download_release(output=target, opener=opener)
        self.assertEqual(len(first["assets"]), 2)
        self.assertFalse((target / "data/fulltext/pdf").exists())
        self.assertTrue((target / "data/derived/corpus.sqlite").is_file())
        self.assertTrue((target / "data/fulltext/PERMISSIONS.json").is_file())
        self.assertFalse(any("-pdf-" in url for url in calls))
        second = download_release(output=target, include_pdfs=True, opener=opener)
        self.assertEqual(len(second["assets"]), 4)
        self.assertEqual(len(list((target / "data/fulltext/pdf").glob("**/*.pdf"))), 2)
        self.assertTrue(all(a["status"] == "cached" for a in second["assets"] if "-pdf-" not in a["name"]))
        third = download_release(output=target, include_pdfs=True, opener=opener)
        self.assertEqual(third["written_files"], 0)
        self.assertTrue(third["unchanged_files"] > 0)

    def test_modified_existing_files_require_explicit_overwrite(self):
        manifest = self.package()
        opener, _, _ = self.fake_api(manifest)
        target = Path(self.temp.name) / "modified"
        target.mkdir()
        (target / "README.md").write_text("local changes")
        with self.assertRaisesRegex(IntegrityError, "existing_file_conflict"):
            download_release(output=target, opener=opener)
        self.assertEqual((target / "README.md").read_text(), "local changes")
        result = download_release(output=target, opener=opener, overwrite=True)
        self.assertGreater(result["written_files"], 0)
        self.assertEqual((target / "README.md").read_text(), (self.root / "README.md").read_text())

    def test_zip_slip_symlinks_and_existing_parent_escape_are_rejected_before_writes(self):
        target = Path(self.temp.name) / "safe-target"
        target.mkdir()
        for name, link in [("../outside.txt", False), ("/absolute.txt", False), ("C:\\escape.txt", False), ("symlink", True)]:
            archive = Path(self.temp.name) / "unsafe.zip"
            info = zipfile.ZipInfo(name)
            if link:
                info.create_system = 3
                info.external_attr = (stat.S_IFLNK | 0o777) << 16
            with zipfile.ZipFile(archive, "w") as output:
                output.writestr(info, b"bad")
            members = [{"path": name, "bytes": 3, "sha256": hashlib.sha256(b"bad").hexdigest()}]
            with self.subTest(name=name), self.assertRaises(IntegrityError):
                extract_archive(archive, target, members)
            self.assertEqual(list(target.iterdir()), [])
        outside = Path(self.temp.name) / "elsewhere"
        outside.mkdir()
        (target / "data").symlink_to(outside)
        archive = Path(self.temp.name) / "parent-escape.zip"
        with zipfile.ZipFile(archive, "w") as output:
            output.writestr("data/escape.txt", b"bad")
        with self.assertRaisesRegex(IntegrityError, "zip_destination_escape"):
            validate_archive(archive, target, [{"path": "data/escape.txt", "bytes": 3, "sha256": hashlib.sha256(b"bad").hexdigest()}])
        self.assertEqual(list(outside.iterdir()), [])

    def test_partial_download_resumes_and_verified_cache_avoids_network(self):
        payload = b"synthetic-asset" * 100
        digest = hashlib.sha256(payload).hexdigest()
        target = Path(self.temp.name) / "cache" / "asset.zip"
        target.parent.mkdir()
        target.with_name("asset.zip.part").write_bytes(payload[:37])
        ranges = []
        def opener(request, **_kwargs):
            ranges.append(request.get_header("Range"))
            return Response(payload[37:], 206, {"Content-Range": f"bytes 37-{len(payload)-1}/{len(payload)}"})
        self.assertEqual(download_asset("https://example.invalid/asset", target, len(payload), digest, opener=opener), "resumed")
        self.assertEqual(ranges, ["bytes=37-"])
        self.assertEqual(target.read_bytes(), payload)
        def forbidden(*_args, **_kwargs):
            self.fail("Verified cache should not download again")
        self.assertEqual(download_asset("https://example.invalid/asset", target, len(payload), digest, opener=forbidden), "cached")

    def test_same_sized_corrupted_asset_is_rejected_and_not_promoted(self):
        payload = b"expected asset bytes"
        target = Path(self.temp.name) / "corrupted.zip"
        opener = lambda *_args, **_kwargs: Response(b"altered! asset bytes")
        with self.assertRaisesRegex(IntegrityError, "asset_checksum_mismatch"):
            download_asset("https://example.invalid/asset", target, len(payload), hashlib.sha256(payload).hexdigest(), opener=opener)
        self.assertFalse(target.exists())
        self.assertFalse(target.with_name(target.name + ".part").exists())


if __name__ == "__main__":
    unittest.main()
