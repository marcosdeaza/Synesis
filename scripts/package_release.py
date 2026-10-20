#!/usr/bin/env python3
"""Create auditable data assets locally. Does not create or publish a GitHub release."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from synesis.fulltext import validate_fulltext

DEFAULT_REPOSITORY = "marcosdeaza/Synesis"
DEFAULT_TAG = "v0.2.0"
MANIFEST_NAME = "synesis-release-manifest.json"
SUMS_NAME = "SHA256SUMS"
CORPUS_REQUIRED = ("catalog.jsonl", "documents.jsonl", "pages.jsonl", "chunks.jsonl", "corpus.sqlite", "corpus_summary.json")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_coordinates(repository: str, tag: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("invalid_repository")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", tag) or ".." in tag:
        raise ValueError("invalid_release_tag")


def _safe_source(root: Path, path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError("unsafe_release_input")
    return resolved


def _read_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def _metadata_files(root: Path) -> list[Path]:
    files = []
    for folder in ("data/research_225", "data/pilot", "docs", "config"):
        base = root / folder
        if base.exists():
            files.extend(path for path in base.rglob("*") if path.is_file()
                         and path.suffix.lower() in {".json", ".jsonl", ".md", ".bib", ".csv", ".cff"}
                         and not any(part.startswith(".") for part in path.relative_to(base).parts))
    for name in ("README.md", "README.en.md", "RIGHTS.md", "LICENSE", "CITATION.cff", "AGENTS.md", "CONTEXTO.md", "CONTEXTO_PUBLICO.md", "PUBLIC_EXPORT_MANIFEST.json"):
        if (root / name).is_file():
            files.append(root / name)
    fulltext = root / "data/fulltext"
    if fulltext.exists():
        files.extend(fulltext.glob("*.json"))
        files.extend(fulltext.glob("*.jsonl"))
        files.extend(fulltext.glob("*.md"))
    reports = root / "reports"
    if reports.exists():
        files.extend(path for path in reports.iterdir() if path.is_file()
                     and path.suffix in {".json", ".csv", ".md"})
    return sorted(set(files), key=lambda path: path.relative_to(root).as_posix())


def _pdf_files(root: Path, known: dict[str, dict]) -> dict[str, list[tuple[Path, str]]]:
    grouped: dict[str, dict[str, tuple[Path, str]]] = defaultdict(dict)
    for name in ("data/fulltext/sources_spain.jsonl", "data/fulltext/sources_global.jsonl"):
        manifest = root / name
        if not manifest.exists():
            continue
        for row in _read_rows(manifest):
            key = row.get("record_id", row.get("id"))
            if key not in known:
                raise ValueError("unknown_pdf_record")
            institution = known[key]["institution_id"]
            if not re.fullmatch(r"[a-z0-9_-]+", institution):
                raise ValueError("invalid_institution_key")
            for entry in row.get("files", []):
                relative = entry.get("path")
                if not isinstance(relative, str) or Path(relative).is_absolute():
                    raise ValueError("unsafe_pdf_path")
                path = _safe_source(root, root / relative)
                expected_root = (root / "data/fulltext/pdf" / institution).resolve()
                if not path.is_relative_to(expected_root) or path.suffix.lower() != ".pdf":
                    raise ValueError("unsafe_pdf_path")
                digest = entry.get("sha256")
                if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
                    raise ValueError("invalid_pdf_checksum")
                if path.stat().st_size != entry.get("bytes") or file_sha256(path) != digest.lower():
                    raise ValueError("pdf_integrity_mismatch")
                grouped[institution][path.relative_to(root).as_posix()] = (path, digest.lower())
    return {institution: [files[key] for key in sorted(files)] for institution, files in sorted(grouped.items())}


def _write_zip(root: Path, output: Path, name: str, sources: list[tuple[Path, str | None]],
               *, stored: bool = False) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".asset-", suffix=".zip", dir=output)
    os.close(descriptor)
    temp = Path(temporary)
    members = []
    try:
        with zipfile.ZipFile(temp, "w", allowZip64=True, compression=zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            seen = set()
            for original, expected in sources:
                path = _safe_source(root, original)
                relative = original.relative_to(root).as_posix()
                if relative in seen:
                    raise ValueError("duplicate_archive_member")
                seen.add(relative)
                info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                info.compress_type = zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED
                info._compresslevel = 6
                digest, size = hashlib.sha256(), 0
                with path.open("rb") as stream, archive.open(info, "w", force_zip64=True) as target:
                    for block in iter(lambda: stream.read(1024 * 1024), b""):
                        target.write(block)
                        digest.update(block)
                        size += len(block)
                checksum = digest.hexdigest()
                if expected is not None and checksum != expected:
                    raise ValueError("input_changed_during_packaging")
                members.append({"path": relative, "bytes": size, "sha256": checksum})
        destination = output / name
        digest, size = file_sha256(temp), temp.stat().st_size
        os.replace(temp, destination)
        return {"name": name, "bytes": size, "sha256": digest, "members": members,
                "uncompressed_bytes": sum(row["bytes"] for row in members)}
    finally:
        temp.unlink(missing_ok=True)


def package_release(root: Path | str = ROOT, output: Path | str | None = None, *,
                    tag: str = DEFAULT_TAG, repository: str = DEFAULT_REPOSITORY,
                    max_part_bytes: int = 250 * 1024 * 1024, include_pdfs: bool = True) -> dict:
    root = Path(root).resolve()
    validate_coordinates(repository, tag)
    if max_part_bytes < 1:
        raise ValueError("invalid_part_size")
    output = Path(output).resolve() if output else root / "release" / tag
    rows = []
    for name in ("spain.jsonl", "global.jsonl"):
        rows.extend(_read_rows(root / "data/research_225" / name))
    known = {row["id"]: row for row in rows}
    if len(known) != len(rows):
        raise ValueError("duplicate_metadata_identity")
    required = [root / "data/derived" / name for name in CORPUS_REQUIRED]
    if not all(path.is_file() for path in required):
        raise ValueError("corpus_artifacts_missing")
    # Use the shared acquisition validator: no unattempted records and no
    # non-final statuses may enter a release, including --no-pdfs exports.
    coverage = validate_fulltext(root, require_files=True, require_complete=True)
    if coverage["attempted_records"] != len(rows):
        raise ValueError("incomplete_release_coverage")
    for name in ("data/research_225/PERMISSIONS.json", "data/fulltext/PERMISSIONS.json"):
        if not (root / name).is_file():
            raise ValueError("permission_record_missing")
    summary = json.loads((root / "data/derived/corpus_summary.json").read_text())
    if summary.get("metadata_records") != len(rows):
        raise ValueError("corpus_catalog_count_mismatch")
    for evidence in summary.get("metadata_inputs", []) + summary.get("source_manifests", []):
        path = root / evidence["path"]
        if not path.is_file() or evidence.get("sha256") != file_sha256(path):
            raise ValueError("corpus_inputs_changed_rebuild_required")
    if len(summary.get("source_manifests", [])) != 2:
        raise ValueError("corpus_source_manifests_missing")
    for artifact in summary.get("outputs", []):
        path = root / "data/derived" / artifact["path"]
        if not path.is_file() or path.stat().st_size != artifact["bytes"] or file_sha256(path) != artifact["sha256"]:
            raise ValueError("corpus_artifact_integrity_mismatch")
    metadata_files = _metadata_files(root)
    derived = required + sorted((root / "data/derived").glob("*.parquet")) + sorted((root / "data/derived").glob("*.csv"))
    pdfs = _pdf_files(root, known) if include_pdfs else {}
    old_assets = set()
    if (output / MANIFEST_NAME).is_file():
        try:
            old = json.loads((output / MANIFEST_NAME).read_text())
            old_assets = {asset["name"] for asset in old.get("assets", [])
                          if isinstance(asset.get("name"), str) and asset["name"].startswith(f"synesis-{tag}-")
                          and asset["name"].endswith(".zip") and "/" not in asset["name"] and "\\" not in asset["name"]}
        except (ValueError, KeyError, TypeError):
            pass
    assets = []
    for kind, paths in (("metadata", metadata_files), ("corpus", derived)):
        asset = _write_zip(root, output, f"synesis-{tag}-{kind}.zip", [(path, None) for path in paths])
        asset["kind"] = kind
        assets.append(asset)
    pdf_count = 0
    for institution, entries in pdfs.items():
        parts, current, size = [], [], 0
        for entry in entries:
            length = entry[0].stat().st_size
            if current and size + length > max_part_bytes:
                parts.append(current)
                current, size = [], 0
            current.append(entry)
            size += length
        if current:
            parts.append(current)
        for index, part in enumerate(parts, 1):
            asset = _write_zip(root, output, f"synesis-{tag}-pdf-{institution}-part{index:03d}.zip", part, stored=True)
            asset.update(kind="pdf", institution_id=institution, part=index, parts=len(parts))
            assets.append(asset)
            pdf_count += len(part)
    base_url = f"https://github.com/{repository}/releases/download/{tag}"
    for asset in assets:
        asset["url"] = f"{base_url}/{asset['name']}"
    manifest = {"schema_version": "1.0", "tag": tag, "repository": repository,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "metadata_records": len(rows), "pdf_files": pdf_count,
                "pdf_target_part_bytes": max_part_bytes,
                "pdf_part_policy": "Uncompressed PDF byte budget; a single larger PDF remains whole.",
                "archive_paths": "Relative to repository root; metadata and corpus selected by default.",
                "manifest_url": f"{base_url}/{MANIFEST_NAME}", "checksums_url": f"{base_url}/{SUMS_NAME}",
                "assets": assets}
    (output / MANIFEST_NAME).write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    sums = [(asset["sha256"], asset["name"]) for asset in assets]
    sums.append((file_sha256(output / MANIFEST_NAME), MANIFEST_NAME))
    (output / SUMS_NAME).write_text("".join(f"{digest}  {name}\n" for digest, name in sums), encoding="utf-8")
    for name in old_assets - {asset["name"] for asset in assets}:
        (output / name).unlink(missing_ok=True)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Preparar paquetes de datos de Synesis sin publicarlos.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--tag", default=DEFAULT_TAG)
    parser.add_argument("--repository", default=DEFAULT_REPOSITORY)
    parser.add_argument("--part-mb", type=float, default=250, help="Objetivo por parte PDF en MiB; no corta un PDF individual.")
    parser.add_argument("--no-pdfs", action="store_true")
    args = parser.parse_args()
    try:
        result = package_release(args.root, args.output, tag=args.tag, repository=args.repository,
                                 max_part_bytes=int(args.part_mb * 1024 * 1024), include_pdfs=not args.no_pdfs)
    except (ValueError, OSError, zipfile.BadZipFile):
        print("release_package_failed: comprobar derivados, manifiestos y checksums locales.", file=sys.stderr)
        return 1
    print(json.dumps({"tag": result["tag"], "metadata_records": result["metadata_records"],
                      "pdf_files": result["pdf_files"], "assets": len(result["assets"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
