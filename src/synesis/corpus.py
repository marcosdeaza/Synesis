"""Traceable, local PDF extraction and lexical retrieval; never labels AI use.

Metadata snapshots and original PDFs are read-only inputs. Offsets address the
normalized page text in pages.jsonl (Unicode code points, half-open intervals).
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import logging
import os
import re
import sqlite3
import tempfile
import unicodedata
import warnings
from collections import Counter, defaultdict
from contextlib import contextmanager
from pathlib import Path
from typing import Callable

SCHEMA_VERSION = "0.2.0"
EXTRACTION_VERSION = "page-nfc-v1"
SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
METADATA_FILES = ("data/research_225/spain.jsonl", "data/research_225/global.jsonl")
SOURCE_FILES = ("data/fulltext/sources_spain.jsonl", "data/fulltext/sources_global.jsonl")


def hash_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def hash_text(value: str) -> str:
    return hash_bytes(value.encode("utf-8"))


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_text(value: object) -> str:
    # JSON permits these separators literally, but common JSONL readers use
    # str.splitlines(); escape them without changing the parsed page text.
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            .replace("\u0085", "\\u0085").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


def normalize_page_text(value: str) -> str:
    """Keep layout newlines; remove NUL only and normalize Unicode deterministically."""
    return unicodedata.normalize("NFC", value.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", ""))


def chunk_text(text: str, max_chars: int = 1800, overlap: int = 200) -> list[tuple[int, int, str]]:
    """Chunk one page only, preserving exact [start, end) offsets in that page."""
    if max_chars < 1 or not 0 <= overlap < max_chars:
        raise ValueError("invalid_chunk_configuration")
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            floor = start + max(max_chars // 2, overlap + 1)
            for separator in ("\n\n", "\n", " "):
                boundary = text.rfind(separator, floor, end)
                if boundary >= floor:
                    end = boundary + len(separator)
                    break
        value = text[start:end]
        if value.strip():
            chunks.append((start, end, value))
        if end == len(text):
            break
        start = max(start + 1, end - overlap)
    return chunks


def _input(path: Path, root: Path) -> tuple[list[dict], dict]:
    raw = path.read_bytes()
    rows = []
    for line in raw.decode("utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError("invalid_jsonl_record")
            rows.append(row)
    return rows, {"path": path.relative_to(root).as_posix(), "sha256": hash_bytes(raw),
                  "bytes": len(raw), "records": len(rows)}


def load_metadata(root: Path, paths: tuple[str, ...] = METADATA_FILES) -> tuple[list[dict], list[dict]]:
    """Load only the complete research snapshot; never concatenate the overlapping pilot."""
    rows, inputs, seen = [], [], set()
    for name in paths:
        values, evidence = _input(root / name, root)
        inputs.append(evidence)
        for row in values:
            key = row.get("id")
            if not isinstance(key, str) or not key or not isinstance(row.get("institution_id"), str):
                raise ValueError("invalid_metadata_identity")
            if key in seen:
                raise ValueError("duplicate_metadata_id")
            seen.add(key)
            rows.append(row)
    return rows, inputs


class FileIssue(ValueError):
    """Stable, non-sensitive error code; never include source text or exception detail."""


def verify_pdf(root: Path, entry: dict) -> Path:
    """Validate a declared PDF without following paths outside the repository."""
    name = entry.get("path")
    expected = entry.get("sha256")
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        raise FileIssue("unsafe_path")
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()):
        raise FileIssue("unsafe_path")
    if path.suffix.lower() != ".pdf":
        raise FileIssue("not_pdf_path")
    if not isinstance(expected, str) or not SHA256.fullmatch(expected):
        raise FileIssue("missing_or_invalid_sha256")
    if not path.is_file():
        raise FileIssue("missing_file")
    declared_bytes = entry.get("bytes")
    if declared_bytes is not None:
        if not isinstance(declared_bytes, int) or isinstance(declared_bytes, bool) or declared_bytes < 0:
            raise FileIssue("invalid_declared_bytes")
        if path.stat().st_size != declared_bytes:
            raise FileIssue("size_mismatch")
    if hash_file(path) != expected.lower():
        raise FileIssue("checksum_mismatch")
    return path


@contextmanager
def _quiet_pdf_parser():
    """Do not leak PDF contents, contact data or parser exception messages to logs."""
    logger = logging.getLogger("pypdf")
    handlers, propagate, level = logger.handlers[:], logger.propagate, logger.level
    logger.handlers = [logging.NullHandler()]
    logger.propagate = False
    logger.setLevel(logging.CRITICAL + 1)
    try:
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter("always")
            yield captured
    finally:
        logger.handlers, logger.propagate, logger.level = handlers, propagate, level


def extractor_version() -> str:
    try:
        return importlib.metadata.version("pypdf")
    except importlib.metadata.PackageNotFoundError:
        return "unavailable"


def extract_pdf(path: Path) -> dict:
    """Read text per page; leave scanned pages empty with an explicit OCR status."""
    try:
        from pypdf import PdfReader
    except ImportError:
        return {"status": "dependency_missing", "error_code": "pypdf_not_installed", "pages": []}
    try:
        with _quiet_pdf_parser() as captured:
            reader = PdfReader(str(path), strict=False)
            if reader.is_encrypted and not reader.decrypt(""):
                return {"status": "encrypted", "error_code": "password_required", "pages": []}
            pages = []
            for index, page in enumerate(reader.pages, 1):
                try:
                    text = normalize_page_text(page.extract_text() or "")
                    status = "text_extracted" if text.strip() else "ocr_needed"
                    error = None
                except Exception:
                    text, status, error = "", "page_error", "page_extraction_failed"
                pages.append({"page_number": index, "text": text, "status": status,
                              "error_code": error, "text_sha256": hash_text(text)})
            warning_count = len(captured)
        nonempty = sum(page["status"] == "text_extracted" for page in pages)
        if not pages:
            status, error = "parse_error", "pdf_has_no_pages"
        elif all(page["status"] == "page_error" for page in pages):
            status, error = "parse_error", "all_pages_failed"
        elif nonempty == len(pages):
            status, error = "text_extracted", None
        elif nonempty:
            status, error = "partial_text", None
        else:
            status, error = "ocr_needed", None
        return {"status": status, "error_code": error, "pages": pages, "warning_count": warning_count}
    except Exception:
        return {"status": "parse_error", "error_code": "pdf_parse_failed", "pages": []}


def _cache_valid(value: object, digest: str, version: str) -> bool:
    if not isinstance(value, dict) or value.get("pdf_sha256") != digest:
        return False
    if value.get("extraction_version") != EXTRACTION_VERSION or value.get("extractor_version") != version:
        return False
    result = value.get("result")
    if not isinstance(result, dict) or result.get("status") not in {"text_extracted", "partial_text", "ocr_needed"}:
        return False
    pages = result.get("pages")
    return isinstance(pages, list) and all(
        isinstance(page, dict) and page.get("page_number") == index
        and isinstance(page.get("text"), str) and page.get("text_sha256") == hash_text(page["text"])
        and page.get("status") in {"text_extracted", "ocr_needed", "page_error"}
        for index, page in enumerate(pages, 1))


def _atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        temp = Path(stream.name)
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write("\n")
    try:
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def _extract_cached(path: Path, digest: str, cache_dir: Path, version: str,
                    extractor: Callable[[Path], dict]) -> tuple[dict, bool]:
    signature = hash_text(EXTRACTION_VERSION + ":" + version)[:16]
    cache = cache_dir / f"{digest}-{signature}.json"
    try:
        value = json.loads(cache.read_text(encoding="utf-8"))
        if _cache_valid(value, digest, version):
            return value["result"], True
    except (OSError, ValueError, TypeError):
        pass
    try:
        result = extractor(path)
    except Exception:
        # Third-party exception messages can include a whole page or an email.
        result = {"status": "parse_error", "error_code": "pdf_parse_failed", "pages": []}
    if hash_file(path) != digest:
        return {"status": "source_changed", "error_code": "source_changed_during_extraction", "pages": []}, False
    value = {"pdf_sha256": digest, "extraction_version": EXTRACTION_VERSION,
             "extractor_version": version, "result": result}
    if _cache_valid(value, digest, version):
        _atomic_json(cache, value)
    return result, False


def _database(path: Path, metadata: list[dict], documents: list[dict], pages: list[dict],
              chunks: list[dict]) -> bool:
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys=ON")
    try:
        connection.executescript("""
        CREATE TABLE metadata (
          record_id TEXT PRIMARY KEY, institution_id TEXT NOT NULL, title TEXT,
          year INTEGER, degree_level TEXT, language TEXT, source_url TEXT,
          academic_date_verified INTEGER, metadata_json TEXT NOT NULL);
        CREATE TABLE documents (
          document_id TEXT PRIMARY KEY, record_id TEXT NOT NULL REFERENCES metadata(record_id),
          work_group_id TEXT NOT NULL, pdf_sha256 TEXT, path TEXT, download_url TEXT,
          status TEXT NOT NULL, error_code TEXT, document_json TEXT NOT NULL);
        CREATE TABLE pages (
          page_id TEXT PRIMARY KEY, document_id TEXT NOT NULL REFERENCES documents(document_id),
          record_id TEXT NOT NULL REFERENCES metadata(record_id), page_number INTEGER NOT NULL,
          status TEXT NOT NULL, text TEXT NOT NULL, text_sha256 TEXT NOT NULL, page_json TEXT NOT NULL);
        CREATE TABLE chunks (
          chunk_id TEXT PRIMARY KEY, document_id TEXT NOT NULL REFERENCES documents(document_id),
          record_id TEXT NOT NULL REFERENCES metadata(record_id), page_id TEXT NOT NULL REFERENCES pages(page_id),
          page_number INTEGER NOT NULL, start_char INTEGER NOT NULL, end_char INTEGER NOT NULL,
          text TEXT NOT NULL, text_sha256 TEXT NOT NULL, chunk_json TEXT NOT NULL);
        CREATE INDEX documents_record ON documents(record_id);
        CREATE INDEX pages_document ON pages(document_id, page_number);
        CREATE INDEX chunks_document_page ON chunks(document_id, page_number, start_char);
        CREATE INDEX metadata_filters ON metadata(institution_id, year, degree_level);
        """)
        connection.executemany("INSERT INTO metadata VALUES (?,?,?,?,?,?,?,?,?)", [
            (row["id"], row["institution_id"], row.get("title"), row.get("year"), row.get("degree_level"),
             row.get("language"), row.get("source_url"), int(row.get("academic_date_verified") is True),
             json_text(row)) for row in metadata])
        connection.executemany("INSERT INTO documents VALUES (?,?,?,?,?,?,?,?,?)", [
            (row["document_id"], row["record_id"], row["work_group_id"], row.get("pdf_sha256"),
             row.get("path"), row.get("download_url"), row["status"], row.get("error_code"), json_text(row))
            for row in documents])
        connection.executemany("INSERT INTO pages VALUES (?,?,?,?,?,?,?,?)", [
            (row["page_id"], row["document_id"], row["record_id"], row["page_number"], row["status"],
             row["text"], row["text_sha256"], json_text(row)) for row in pages])
        connection.executemany("INSERT INTO chunks VALUES (?,?,?,?,?,?,?,?,?,?)", [
            (row["chunk_id"], row["document_id"], row["record_id"], row["page_id"], row["page_number"],
             row["start_char"], row["end_char"], row["text"], row["text_sha256"], json_text(row)) for row in chunks])
        try:
            connection.execute("CREATE VIRTUAL TABLE chunks_fts USING fts5(text, content='chunks', content_rowid='rowid', tokenize='unicode61 remove_diacritics 2')")
            connection.execute("INSERT INTO chunks_fts(chunks_fts) VALUES ('rebuild')")
            fts = True
        except sqlite3.OperationalError as error:
            if "no such module" not in str(error).lower():
                raise
            fts = False
        connection.execute("CREATE TABLE corpus_info (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        connection.executemany("INSERT INTO corpus_info VALUES (?,?)", [
            ("schema_version", SCHEMA_VERSION), ("fts5_available", json_text(fts)),
            ("offset_unit", "Unicode code points in normalized page text; [start,end)")])
        connection.commit()
        return fts
    finally:
        connection.close()


def build_corpus(root: Path | str, output_dir: Path | str | None = None, *, max_chars: int = 1800,
                 overlap: int = 200, metadata_paths: tuple[str, ...] = METADATA_FILES,
                 source_paths: tuple[str, ...] = SOURCE_FILES,
                 extractor: Callable[[Path], dict] | None = None) -> dict:
    """Build catalog + page/chunk JSONL + SQLite from the frozen metadata and PDF manifests.

    Missing source manifests are acceptable while harvesting is in progress.
    A PDF failure never prevents unrelated documents from being indexed.
    ``extractor`` is an injection point for synthetic software fixtures only.
    """
    chunk_text("", max_chars, overlap)  # Validate even when no PDF has been downloaded.
    root = Path(root).resolve()
    output = Path(output_dir).resolve() if output_dir else root / "data/derived"
    metadata, metadata_inputs = load_metadata(root, metadata_paths)
    known = {row["id"]: row for row in metadata}
    sources: dict[str, list[dict]] = defaultdict(list)
    source_inputs, issues = [], Counter()
    for name in source_paths:
        path = root / name
        if not path.exists():
            source_inputs.append({"path": name, "status": "not_created"})
            continue
        try:
            rows, evidence = _input(path, root)
            source_inputs.append(evidence)
        except (ValueError, OSError, UnicodeError):
            source_inputs.append({"path": name, "status": "invalid_manifest"})
            issues["invalid_source_manifest"] += 1
            continue
        for row in rows:
            key = row.get("record_id", row.get("id"))
            if not isinstance(key, str) or key not in known:
                issues["unknown_manifest_record"] += 1
                continue
            sources[key].append(row)
    output.mkdir(parents=True, exist_ok=True)
    cache_dir = output / ".cache"
    version = extractor_version() if extractor is None else "fixture-injected"
    extract = extract_pdf if extractor is None else extractor
    documents, pages, chunks, catalog = [], [], [], []
    cache_hits, cache_misses, source_statuses = 0, 0, Counter()
    for row in metadata:
        key = row["id"]
        candidates = []
        status_values = []
        for source in sources.get(key, []):
            status = source.get("status", "unspecified")
            if isinstance(status, str):
                status_values.append(status)
                source_statuses[status] += 1
            values = source.get("files", [])
            if not isinstance(values, list):
                issues["invalid_file_list"] += 1
                continue
            for entry in values:
                if isinstance(entry, dict):
                    candidates.append((entry, source))
                else:
                    issues["invalid_file_manifest"] += 1
        groups: dict[str, list[tuple[dict, dict]]] = defaultdict(list)
        for entry, source in candidates:
            sha = entry.get("sha256")
            group = sha.lower() if isinstance(sha, str) and SHA256.fullmatch(sha) else "invalid-" + hash_text(json_text(entry))
            groups[group].append((entry, source))
        own_documents = []
        for group, alternatives in sorted(groups.items()):
            selected = None
            first_error = None
            for entry, source in alternatives:
                try:
                    path = verify_pdf(root, entry)
                    selected = (entry, source, path)
                    break
                except FileIssue as error:
                    code = str(error)
                except OSError:
                    code = "file_read_failed"
                issues[code] += 1
                first_error = first_error or code
            entry, source = alternatives[0] if selected is None else selected[:2]
            digest = group if SHA256.fullmatch(group) else None
            document_id = "doc-" + hash_text(key + "\0" + group)[:32]
            document = {"document_id": document_id, "record_id": key, "work_group_id": key,
                        "pdf_sha256": digest, "path": entry.get("path") if selected else None,
                        "download_url": entry.get("download_url"), "source_url": row.get("source_url"),
                        "source_license": entry.get("source_license", source.get("source_license")),
                        "source_license_url": entry.get("source_license_url", entry.get("license_evidence_url", source.get("source_license_url", source.get("license_evidence_url")))),
                        "metadata_work_license": row.get("license"),
                        "role": entry.get("role", entry.get("kind", "unspecified")),
                        "manifest_entries": len(alternatives), "status": first_error,
                        "error_code": first_error, "page_count": 0, "text_page_count": 0,
                        "character_count": 0, "extractor": "pypdf", "extractor_version": version,
                        "extraction_version": EXTRACTION_VERSION}
            if selected:
                try:
                    result, hit = _extract_cached(selected[2], digest, cache_dir, version, extract)
                    actual_size = selected[2].stat().st_size
                except OSError:
                    result = {"status": "file_read_failed", "error_code": "file_read_failed", "pages": []}
                    hit, actual_size = False, None
                cache_hits += int(hit)
                cache_misses += int(not hit)
                document["status"] = result.get("status", "parse_error")
                document["error_code"] = result.get("error_code")
                if document["error_code"]:
                    issues[document["error_code"]] += 1
                document["bytes"] = actual_size
                document["parser_warning_count"] = result.get("warning_count", 0)
                document["page_count"] = len(result.get("pages", []))
                for value in result.get("pages", []):
                    number = value["page_number"]
                    text = value["text"]
                    page_id = f"{document_id}:p{number}"
                    page = {"page_id": page_id, "document_id": document_id, "record_id": key,
                            "work_group_id": key, "page_number": number, "text": text,
                            "text_sha256": hash_text(text), "character_count": len(text),
                            "status": value["status"], "error_code": value.get("error_code"),
                            "pdf_sha256": digest, "pdf_path": entry["path"],
                            "source_url": row.get("source_url"), "download_url": entry.get("download_url"),
                            "source_license": document["source_license"],
                            "license_evidence_url": document["source_license_url"]}
                    pages.append(page)
                    if value.get("error_code"):
                        issues[value["error_code"]] += 1
                    document["text_page_count"] += int(value["status"] == "text_extracted")
                    document["character_count"] += len(text)
                    for start, end, text_chunk in chunk_text(text, max_chars, overlap):
                        sha = hash_text(text_chunk)
                        chunk_id = "chunk-" + hash_text(f"{page_id}:{start}:{end}:{sha}")[:40]
                        chunks.append({"chunk_id": chunk_id, "document_id": document_id,
                                       "record_id": key, "work_group_id": key, "page_id": page_id,
                                       "page_number": number, "start_char": start, "end_char": end,
                                       "offset_unit": "unicode_code_points", "text": text_chunk,
                                       "text_sha256": sha, "page_text_sha256": page["text_sha256"],
                                       "pdf_sha256": digest, "pdf_path": entry["path"],
                                       "source_url": page["source_url"], "download_url": page["download_url"],
                                       "source_license": document["source_license"],
                            "license_evidence_url": document["source_license_url"]})
            documents.append(document)
            own_documents.append(document)
        has_text = any(doc["text_page_count"] for doc in own_documents)
        verified = [doc for doc in own_documents if doc["status"] in {"text_extracted", "partial_text", "ocr_needed", "parse_error", "encrypted", "dependency_missing"} and doc.get("bytes") is not None]
        if has_text:
            fulltext_status = "text_extracted" if all(doc["status"] == "text_extracted" for doc in own_documents) else "partial_text"
        elif any(doc["status"] == "ocr_needed" for doc in own_documents):
            fulltext_status = "ocr_needed"
        elif own_documents:
            fulltext_status = "unusable_pdf"
        else:
            fulltext_status = "not_downloaded"
        catalog.append({"record_id": key, "metadata": row, "fulltext_status": fulltext_status,
                        "source_statuses": sorted(set(status_values)),
                        "document_ids": [doc["document_id"] for doc in own_documents],
                        "pdf_document_count": len(own_documents), "verified_pdf_count": len(verified),
                        "text_page_count": sum(doc["text_page_count"] for doc in own_documents),
                        "work_group_id": key})
    with tempfile.TemporaryDirectory(prefix=".build-", dir=output) as folder:
        stage = Path(folder)
        for name, values in (("catalog.jsonl", catalog), ("documents.jsonl", documents),
                             ("pages.jsonl", pages), ("chunks.jsonl", chunks)):
            with (stage / name).open("w", encoding="utf-8") as stream:
                for value in values:
                    stream.write(json_text(value) + "\n")
        fts = _database(stage / "corpus.sqlite", metadata, documents, pages, chunks)
        output_names = ["catalog.jsonl", "documents.jsonl", "pages.jsonl", "chunks.jsonl", "corpus.sqlite"]
        outputs = [{"path": name, "sha256": hash_file(stage / name), "bytes": (stage / name).stat().st_size}
                   for name in output_names]
        summary = {"schema_version": SCHEMA_VERSION, "metadata_records": len(metadata),
                   "records_with_source_manifest": len(sources),
                   "records_with_verified_pdf": sum(row["verified_pdf_count"] > 0 for row in catalog),
                   "records_with_text": sum(row["text_page_count"] > 0 for row in catalog),
                   "document_count": len(documents), "page_count": len(pages), "chunk_count": len(chunks),
                   "character_count": sum(page["character_count"] for page in pages),
                   "document_status_counts": dict(sorted(Counter(row["status"] for row in documents).items())),
                   "catalog_status_counts": dict(sorted(Counter(row["fulltext_status"] for row in catalog).items())),
                   "page_status_counts": dict(sorted(Counter(row["status"] for row in pages).items())),
                   "source_status_counts": dict(sorted(source_statuses.items())),
                   "issue_counts": dict(sorted(issues.items())), "fts5_available": fts,
                   "cache_hits": cache_hits, "cache_misses": cache_misses,
                   "extractor": "pypdf", "extractor_version": version, "extraction_version": EXTRACTION_VERSION,
                   "chunk_max_chars": max_chars, "chunk_overlap": overlap,
                   "metadata_inputs": metadata_inputs, "source_manifests": source_inputs,
                   "outputs": outputs, "pilot_records_added": 0,
                   "offsets": "Unicode code points in normalized page text; zero-based [start,end)",
                   "training_performed": False, "ai_use_labels_created": False}
        _atomic_json(stage / "corpus_summary.json", summary)
        for name in output_names + ["corpus_summary.json"]:
            os.replace(stage / name, output / name)
    return summary


def search_corpus(database: Path | str, query: str, limit: int = 10, *, institution: str | None = None,
                  degree: str | None = None, year_min: int | None = None,
                  year_max: int | None = None, literal: bool = False) -> dict:
    """Read-only lexical search. Result excerpts are requested content, not diagnostic logs."""
    if not isinstance(query, str) or not query.strip():
        return {"engine": "none", "results": []}
    if not 1 <= limit <= 1000:
        raise ValueError("invalid_search_limit")
    path = Path(database).resolve()
    if not path.is_file():
        raise ValueError("corpus_database_missing")
    connection = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        fts = connection.execute("SELECT 1 FROM sqlite_master WHERE name='chunks_fts'").fetchone() is not None
        filters, values = [], []
        if institution is not None:
            filters.append("m.institution_id = ?")
            values.append(institution)
        if degree is not None:
            filters.append("m.degree_level = ?")
            values.append(degree)
        if year_min is not None:
            filters.append("m.year >= ?")
            values.append(year_min)
        if year_max is not None:
            filters.append("m.year <= ?")
            values.append(year_max)
        where = "".join(" AND " + value for value in filters)
        columns = "c.chunk_id,c.record_id,c.document_id,c.page_id,c.page_number,c.start_char,c.end_char,c.text_sha256,m.title,m.institution_id,m.year,m.degree_level,m.source_url,d.path AS pdf_path,d.pdf_sha256,d.download_url,d.document_json"
        if fts:
            match = '"' + query.replace('"', '""') + '"' if literal else query
            sql = f"SELECT {columns}, snippet(chunks_fts,0,'[',']',' … ',32) AS excerpt, bm25(chunks_fts) AS score FROM chunks_fts JOIN chunks c ON c.rowid=chunks_fts.rowid JOIN metadata m ON m.record_id=c.record_id JOIN documents d ON d.document_id=c.document_id WHERE chunks_fts MATCH ?{where} ORDER BY score,c.chunk_id LIMIT ?"
            params = [match, *values, limit]
        else:
            escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            sql = f"SELECT {columns}, substr(c.text,1,320) AS excerpt, NULL AS score FROM chunks c JOIN metadata m ON m.record_id=c.record_id JOIN documents d ON d.document_id=c.document_id WHERE c.text LIKE ? ESCAPE '\\'{where} ORDER BY c.record_id,c.page_number,c.start_char LIMIT ?"
            params = ["%" + escaped + "%", *values, limit]
        try:
            results = [dict(row) for row in connection.execute(sql, params)]
        except sqlite3.OperationalError:
            raise ValueError("invalid_search_query") from None
        for result in results:
            document = json.loads(result.pop("document_json"))
            result["source_license"] = document.get("source_license")
            result["license_evidence_url"] = document.get("source_license_url")
        return {"engine": "fts5" if fts else "literal_like_fallback", "results": results}
    finally:
        connection.close()
