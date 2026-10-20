#!/usr/bin/env python3
"""Download public release data, verify checksums and reject unsafe ZIP members."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_NAME = "synesis-release-manifest.json"
SUMS_NAME = "SHA256SUMS"
DEFAULT_REPOSITORY = "marcosdeaza/Synesis"
DEFAULT_TAG = "v0.2.0"


class IntegrityError(ValueError):
    pass


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _name(value: object) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", value) or ".." in value:
        raise IntegrityError("unsafe_asset_name")
    return value


def _request(url: str, offset: int = 0) -> urllib.request.Request:
    headers = {"User-Agent": "SynesisPublicData/0.2", "Accept": "application/vnd.github+json" if url.startswith("https://api.github.com/") else "application/octet-stream"}
    if offset:
        headers["Range"] = f"bytes={offset}-"
    return urllib.request.Request(url, headers=headers)


def _fetch(url: str, opener, maximum: int = 16 * 1024 * 1024) -> bytes:
    with opener(_request(url), timeout=60) as response:
        value = response.read(maximum + 1)
    if len(value) > maximum:
        raise IntegrityError("release_metadata_too_large")
    return value


def _small_asset(asset: dict, opener) -> bytes:
    raw = _fetch(asset["browser_download_url"], opener)
    if len(raw) != asset.get("size"):
        raise IntegrityError("release_metadata_size_mismatch")
    digest = asset.get("digest")
    if isinstance(digest, str) and digest.startswith("sha256:") and hashlib.sha256(raw).hexdigest() != digest[7:]:
        raise IntegrityError("github_asset_digest_mismatch")
    return raw


def download_asset(url: str, destination: Path, size: int, digest: str, *, opener=None, attempts: int = 3) -> str:
    """Reuse verified files and resume .part only when the server honors Range."""
    opener = opener or urllib.request.urlopen
    if not isinstance(size, int) or isinstance(size, bool) or size < 0 or not re.fullmatch(r"[a-f0-9]{64}", digest):
        raise IntegrityError("invalid_asset_integrity_metadata")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.is_file() and destination.stat().st_size == size and file_sha256(destination) == digest:
        return "cached"
    partial = destination.with_name(destination.name + ".part")
    for _ in range(attempts):
        offset = partial.stat().st_size if partial.is_file() else 0
        if offset > size:
            partial.unlink()
            offset = 0
        if offset == size:
            if file_sha256(partial) == digest:
                os.replace(partial, destination)
                return "resumed"
            partial.unlink()
            offset = 0
        try:
            with opener(_request(url, offset), timeout=120) as response:
                status = getattr(response, "status", None) or response.getcode()
                append = offset > 0 and status == 206
                if status == 206:
                    content_range = response.headers.get("Content-Range", "")
                    match = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", content_range)
                    if not match or int(match[1]) != offset or int(match[3]) != size:
                        raise IntegrityError("invalid_resume_range")
                elif status != 200:
                    raise IntegrityError("unexpected_download_response")
                if not append:
                    offset = 0
                with partial.open("ab" if append else "wb") as target:
                    length = offset
                    while True:
                        block = response.read(1024 * 1024)
                        if not block:
                            break
                        length += len(block)
                        if length > size:
                            raise IntegrityError("asset_size_exceeded")
                        target.write(block)
            if partial.stat().st_size != size:
                continue
            if file_sha256(partial) != digest:
                partial.unlink(missing_ok=True)
                raise IntegrityError("asset_checksum_mismatch")
            os.replace(partial, destination)
            return "resumed" if append else "downloaded"
        except urllib.error.HTTPError as error:
            if error.code == 416:
                partial.unlink(missing_ok=True)
                continue
            if error.code not in {408, 429, 500, 502, 503, 504}:
                raise IntegrityError(f"download_http_{error.code}") from None
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            continue
    raise IntegrityError("asset_download_incomplete")


def _relative(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise IntegrityError("unsafe_zip_path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or re.match(r"^[A-Za-z]:", value):
        raise IntegrityError("unsafe_zip_path")
    return path


def validate_archive(path: Path, output: Path, members: list[dict]) -> list[zipfile.ZipInfo]:
    """Preflight every path and member before writing any extracted file."""
    output = output.resolve()
    expected = {}
    for row in members:
        name = _relative(row["path"]).as_posix()
        if name in expected:
            raise IntegrityError("duplicate_manifest_member")
        expected[name] = row
    with zipfile.ZipFile(path) as archive:
        infos, seen, folded = archive.infolist(), set(), set()
        for info in infos:
            name = _relative(info.filename).as_posix()
            if "\x00" in getattr(info, "orig_filename", info.filename):
                raise IntegrityError("unsafe_zip_path")
            if name in seen or name.casefold() in folded:
                raise IntegrityError("duplicate_zip_path")
            seen.add(name)
            folded.add(name.casefold())
            mode = info.external_attr >> 16
            kind = stat.S_IFMT(mode)
            if stat.S_ISLNK(mode) or kind not in {0, stat.S_IFREG, stat.S_IFDIR}:
                raise IntegrityError("unsafe_zip_file_type")
            target = (output / name).resolve()
            if not target.is_relative_to(output):
                raise IntegrityError("zip_destination_escape")
            if info.is_dir():
                continue
            if name not in expected or info.file_size != expected[name]["bytes"]:
                raise IntegrityError("archive_member_mismatch")
            if not re.fullmatch(r"[a-f0-9]{64}", expected[name].get("sha256", "")):
                raise IntegrityError("invalid_member_checksum")
        regular = {info.filename for info in infos if not info.is_dir()}
        if regular != set(expected):
            raise IntegrityError("archive_member_set_mismatch")
        return infos


def extract_archive(path: Path, output: Path, members: list[dict], *, overwrite: bool = False) -> dict:
    infos = validate_archive(path, output, members)
    expected = {row["path"]: row for row in members}
    output = output.resolve()
    # No partial extraction when an existing modified file would be overwritten.
    for info in infos:
        if info.is_dir():
            continue
        target = output / info.filename
        row = expected[info.filename]
        if target.exists() and not overwrite:
            if not target.is_file() or target.stat().st_size != row["bytes"] or file_sha256(target) != row["sha256"]:
                raise IntegrityError("existing_file_conflict")
    written, skipped = 0, 0
    with zipfile.ZipFile(path) as archive:
        for info in infos:
            target = output / info.filename
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            row = expected[info.filename]
            if target.is_file() and target.stat().st_size == row["bytes"] and file_sha256(target) == row["sha256"]:
                skipped += 1
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            descriptor, name = tempfile.mkstemp(prefix=".synesis-extract-", dir=target.parent)
            os.close(descriptor)
            temp = Path(name)
            digest, size = hashlib.sha256(), 0
            try:
                with archive.open(info) as stream, temp.open("wb") as destination:
                    for block in iter(lambda: stream.read(1024 * 1024), b""):
                        destination.write(block)
                        digest.update(block)
                        size += len(block)
                if size != row["bytes"] or digest.hexdigest() != row["sha256"]:
                    raise IntegrityError("extracted_member_checksum_mismatch")
                if not target.resolve().is_relative_to(output):
                    raise IntegrityError("zip_destination_escape")
                os.replace(temp, target)
                written += 1
            finally:
                temp.unlink(missing_ok=True)
    return {"written_files": written, "unchanged_files": skipped}


def download_release(repository: str = DEFAULT_REPOSITORY, tag: str = DEFAULT_TAG,
                     output: Path | str = ROOT, *, include_pdfs: bool = False,
                     cache: Path | str | None = None, overwrite: bool = False, opener=None) -> dict:
    opener = opener or urllib.request.urlopen
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise IntegrityError("invalid_repository")
    _name(tag)
    output = Path(output).resolve()
    cache = Path(cache).resolve() if cache else output / "release/downloads" / tag
    release = json.loads(_fetch(f"https://api.github.com/repos/{repository}/releases/tags/{tag}", opener))
    assets = {row["name"]: row for row in release.get("assets", [])}
    if MANIFEST_NAME not in assets or SUMS_NAME not in assets:
        raise IntegrityError("release_integrity_assets_missing")
    manifest_raw = _small_asset(assets[MANIFEST_NAME], opener)
    sums_raw = _small_asset(assets[SUMS_NAME], opener)
    checksums = {}
    for line in sums_raw.decode("utf-8").splitlines():
        match = re.fullmatch(r"([a-f0-9]{64})  (.+)", line)
        if not match:
            raise IntegrityError("invalid_checksum_list")
        name = _name(match[2])
        if name in checksums:
            raise IntegrityError("duplicate_checksum_entry")
        checksums[name] = match[1]
    if checksums.get(MANIFEST_NAME) != hashlib.sha256(manifest_raw).hexdigest():
        raise IntegrityError("manifest_checksum_mismatch")
    manifest = json.loads(manifest_raw)
    if manifest.get("repository") != repository or manifest.get("tag") != tag:
        raise IntegrityError("release_identity_mismatch")
    base_url = f"https://github.com/{repository}/releases/download/{tag}"
    selected, names, member_names = [], set(), set()
    for asset in manifest.get("assets", []):
        name = _name(asset["name"])
        if name in names:
            raise IntegrityError("duplicate_release_asset")
        names.add(name)
        if asset.get("kind") not in {"metadata", "corpus", "pdf"}:
            raise IntegrityError("unknown_asset_kind")
        if asset["kind"] == "pdf" and not include_pdfs:
            continue
        public = assets.get(name)
        expected_url = f"{base_url}/{name}"
        if public is None or public.get("browser_download_url") != expected_url or asset.get("url") != expected_url:
            raise IntegrityError("asset_url_mismatch")
        if public.get("size") != asset.get("bytes") or checksums.get(name) != asset.get("sha256"):
            raise IntegrityError("asset_integrity_metadata_mismatch")
        for row in asset.get("members", []):
            relative = _relative(row["path"]).as_posix()
            if relative.casefold() in member_names:
                raise IntegrityError("overlapping_archive_members")
            member_names.add(relative.casefold())
        selected.append(asset)
    if not {"metadata", "corpus"}.issubset({asset["kind"] for asset in selected}):
        raise IntegrityError("required_data_assets_missing")
    cache.mkdir(parents=True, exist_ok=True)
    (cache / MANIFEST_NAME).write_bytes(manifest_raw)
    (cache / SUMS_NAME).write_bytes(sums_raw)
    downloads = []
    for asset in selected:
        path = cache / asset["name"]
        status = download_asset(asset["url"], path, asset["bytes"], asset["sha256"], opener=opener)
        validate_archive(path, output, asset["members"])
        downloads.append({"name": asset["name"], "status": status, "bytes": asset["bytes"]})
    output.mkdir(parents=True, exist_ok=True)
    written, unchanged = 0, 0
    for asset in selected:
        counts = extract_archive(cache / asset["name"], output, asset["members"], overwrite=overwrite)
        written += counts["written_files"]
        unchanged += counts["unchanged_files"]
    return {"repository": repository, "tag": tag, "pdfs_requested": include_pdfs,
            "assets": downloads, "written_files": written, "unchanged_files": unchanged,
            "integrity": "SHA-256 + bytes + ZIP member checks; not a digital signature"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Descargar y verificar datos públicos de una release de Synesis.")
    parser.add_argument("--repository", default=DEFAULT_REPOSITORY)
    parser.add_argument("--tag", default=DEFAULT_TAG)
    parser.add_argument("--output", type=Path, default=ROOT)
    parser.add_argument("--cache", type=Path)
    parser.add_argument("--pdfs", action="store_true", help="Incluir originales PDF; por defecto solo metadatos y corpus.")
    parser.add_argument("--overwrite", action="store_true", help="Permitir sustituir archivos locales modificados.")
    args = parser.parse_args()
    try:
        result = download_release(args.repository, args.tag, args.output, include_pdfs=args.pdfs,
                                  cache=args.cache, overwrite=args.overwrite)
    except (ValueError, KeyError, OSError, zipfile.BadZipFile, urllib.error.URLError):
        print("release_download_failed: comprobar release, integridad, rutas y conflictos locales; no se muestran contenidos en logs.", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
