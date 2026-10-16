"""Small, offline and dependency-free transformations for the pilot."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

REQUIRED = {"id", "institution_id", "title", "year", "degree_level", "source_url",
            "record_identifier", "retrieved_at", "evidence_kind", "date_precision"}
# Public connector outputs are deliberately closed: new fields need explicit review.
PUBLIC_FIELDS = REQUIRED | {
    "abstract", "abstract_available", "abstract_omitted_by_policy", "access_rights",
    "accessioned_raw", "campus", "campus_evidence_url", "created_raw", "date_evidence",
    "date_semantics", "degree_evidence", "issued_raw", "language", "license",
    "metadata_license", "metadata_license_evidence_url", "rights_statement", "subjects",
    "rights_raw", "date_candidates_raw", "adapter", "rights_reference_url",
    "academic_date_verified",
}
STRING_FIELDS = {"id", "institution_id", "title", "source_url", "record_identifier",
                 "retrieved_at", "degree_level", "date_precision", "evidence_kind"}
LIST_FIELDS = {"subjects", "rights_raw", "date_candidates_raw"}
BOOL_FIELDS = {"abstract_available", "abstract_omitted_by_policy", "academic_date_verified"}
URL_FIELDS = {"source_url", "campus_evidence_url", "license",
              "metadata_license_evidence_url", "rights_reference_url"}
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
MAX_YEAR = 2026  # This release is a fixed research snapshot, not a rolling cutoff.
# These are lexical mentions, never authorship or evidence of actual tool use.
CUES = {
    "named_assistant": r"\b(?:chatgpt|gpt[ -]?\d+(?:\.\d+)*(?:[a-z][a-z0-9]*)?(?:[- ](?:turbo|mini|nano|pro))?|claude code|github copilot|microsoft copilot|google gemini|anthropic claude)\b",
    "generative_ai": r"\b(?:generative (?:ai|artificial intelligence)|inteligencia artificial generativa|ia generativa|generative ki)\b|生成式人工智能",
    "language_model": r"\b(?:large language models?|llms?|modelos? de lenguaje|modelos? de linguagem|sprachmodelle?)\b|大语言模型|大型語言模型",
    "retrieval_augmented": r"\b(?:retrieval[ -]augmented generation|generaci[oó]n aumentada por recuperaci[oó]n)\b",
    "agentic": r"\b(?:agentic|autonomous (?:ai )?agents?|agentes? aut[oó]nomos?)\b",
}
AMBIGUOUS_ASSISTANT = r"\b(?:claude|copilot|gemini)\b"
ASSISTANT_CONTEXT = r"\b(?:ai|ia|llms?|generative|generativa|anthropic|chatbots?|assistants?|asistentes?)\b|artificial intelligence|inteligencia artificial"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def metadata_date(value: str | None) -> tuple[int | None, str]:
    """Validate the complete date without inventing missing calendar precision."""
    if not isinstance(value, str):
        return None, "unknown"
    text = value.strip()
    if re.fullmatch(r"\d{4}(?:[-/]\d{2})?(?:[-/]\d{2})?", text):
        normalized = text.replace("/", "-")
        formats = {4: ("%Y", "year"), 7: ("%Y-%m", "month"), 10: ("%Y-%m-%d", "day")}
        fmt, precision = formats[len(normalized)]
        try:
            parsed = datetime.strptime(normalized, fmt)
        except ValueError:
            return None, "unknown"
    elif re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?", text):
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None, "unknown"
        precision = "day"
    else:
        return None, "unknown"
    return (parsed.year, precision) if 1800 <= parsed.year <= MAX_YEAR else (None, "unknown")


def valid_url(value: object) -> bool:
    if not isinstance(value, str) or any(c.isspace() for c in value):
        return False
    try:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.hostname) and not parsed.username and not parsed.password
    except ValueError:
        return False


def validate_record(row: object) -> list[str]:
    if not isinstance(row, dict):
        return ["invalid_record_object"]
    errors = [f"missing:{key}" for key in sorted(REQUIRED - row.keys())]
    errors.extend(f"unapproved_public_field:{key}" for key in sorted(set(row) - PUBLIC_FIELDS, key=str))
    for key in STRING_FIELDS & row.keys():
        if not isinstance(row[key], str) or not row[key].strip():
            errors.append(f"invalid_string:{key}")
    for key in LIST_FIELDS & row.keys():
        if not isinstance(row[key], list) or any(not isinstance(item, str) for item in row[key]):
            errors.append(f"invalid_string_list:{key}")
    for key in BOOL_FIELDS & row.keys():
        if not isinstance(row[key], bool):
            errors.append(f"invalid_boolean:{key}")
    nullable_strings = PUBLIC_FIELDS - REQUIRED - LIST_FIELDS - BOOL_FIELDS
    for key in nullable_strings & row.keys():
        if row[key] is not None and not isinstance(row[key], str):
            errors.append(f"invalid_nullable_string:{key}")
    if row.get("degree_level") not in ("bachelor", "master", "unknown"):
        errors.append("invalid_degree")
    if row.get("date_precision") not in ("year", "month", "day", "unknown"):
        errors.append("invalid_date_precision")
    year = row.get("year")
    if year is not None and (not isinstance(year, int) or isinstance(year, bool) or not 1800 <= year <= MAX_YEAR):
        errors.append("invalid_year")
    if (year is None) != (row.get("date_precision") == "unknown"):
        errors.append("inconsistent_date_precision")
    for key in URL_FIELDS & row.keys():
        if (key == "source_url" or row[key] is not None) and not valid_url(row[key]):
            errors.append(f"invalid_url:{key}")
    if row.get("evidence_kind") != "metadata":
        errors.append("unsupported_evidence_kind")
    stamp = row.get("retrieved_at")
    if isinstance(stamp, str):
        try:
            datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        except ValueError:
            errors.append("invalid_retrieved_at")
    if row.get("abstract_omitted_by_policy") is True and row.get("abstract") is not None:
        errors.append("abstract_present_despite_omission_policy")
    # Catch accidental contact data even inside an approved text/list field.
    if EMAIL.search(json.dumps(row, ensure_ascii=False, default=str)):
        errors.append("email_in_public_metadata")
    return errors


def normalized_title(title: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", title).casefold().split())


def mention_features(row: dict) -> dict:
    """Count evidence in available metadata. A negative result means 'not found'."""
    abstract = "" if row.get("abstract_omitted_by_policy") else row.get("abstract") or ""
    text = " ".join([row.get("title", ""), abstract, " ".join(row.get("subjects") or [])])
    result = {name: bool(re.search(pattern, text, flags=re.I)) for name, pattern in CUES.items()}
    if re.search(AMBIGUOUS_ASSISTANT, text, re.I) and re.search(ASSISTANT_CONTEXT, text, re.I):
        result["named_assistant"] = True
    # Classical autonomous agents predate generative models: require such context.
    result["agentic"] = result["agentic"] and any(result[k] for k in CUES if k != "agentic")
    result["any_ai_cue"] = any(result.values())
    result["metadata_chars"] = len(text)
    result["abstract_available"] = bool(row.get("abstract_available") or row.get("abstract"))
    result["abstract_text_analyzed"] = bool(abstract)
    return result


def period(year: int | None) -> str:
    # Year-only metadata cannot locate a thesis relative to a November event.
    if year is None:
        return "undated"
    if year <= 2021:
        return "pre_2022"
    if year in {2022, 2023}:
        return "transition_2022_2023"
    return "post_2024"


def curate(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    accepted, issues, seen_identifiers, seen_ids = [], [], set(), set()
    for row in rows:
        errors = validate_record(row)
        if errors:
            issue_id = row.get("id") if isinstance(row, dict) else None
            if not isinstance(issue_id, str) or EMAIL.search(issue_id):
                issue_id = None
            issues.append({"id": issue_id, "issues": errors})
            continue
        key = (row["institution_id"], row["record_identifier"])
        if key in seen_identifiers:
            errors.append("duplicate_identifier")
        if row["id"] in seen_ids:
            errors.append("duplicate_id")
        if errors:
            issues.append({"id": row["id"], "issues": errors})
            continue
        seen_identifiers.add(key)
        seen_ids.add(row["id"])
        value = dict(row)
        value.update(mention_features(row))
        value["period"] = period(row["year"])
        value["title_fingerprint"] = hashlib.sha256(normalized_title(row["title"]).encode()).hexdigest()[:16]
        value["eligible_level"] = row["degree_level"] in {"bachelor", "master"}
        value["ai_use_status"] = "not_assessed"
        accepted.append(value)
    return sorted(accepted, key=lambda r: (r["institution_id"], r.get("year") or 0, r["id"])), issues


def wilson(k: int, n: int) -> tuple[float, float] | None:
    """95% Wilson interval; sampling bias is NOT corrected by this interval."""
    if n == 0:
        return None
    z = 1.959963984540054
    center = (k/n + z*z/(2*n))/(1+z*z/n)
    half = z*((k/n*(1-k/n)/n + z*z/(4*n*n))**0.5)/(1+z*z/n)
    return center-half, center+half


def summary(rows: list[dict]) -> dict:
    eligible = [r for r in rows if r["eligible_level"]]
    institutions = []
    for iid in sorted({r["institution_id"] for r in rows}):
        group = [r for r in rows if r["institution_id"] == iid]
        valid = [r for r in group if r["eligible_level"]]
        years = [r["year"] for r in valid if r["year"] is not None]
        institutions.append({"institution_id": iid, "records": len(group), "eligible": len(valid),
            "abstracts": sum(r["abstract_available"] for r in valid),
            "abstracts_analyzed": sum(r["abstract_text_analyzed"] for r in valid),
            "cue_mentions": sum(r["any_ai_cue"] for r in valid),
            "min_year": min(years) if years else None, "max_year": max(years) if years else None})
    cells = []
    for iid, per in sorted({(r["institution_id"], r["period"]) for r in eligible}):
        group = [r for r in eligible if r["institution_id"] == iid and r["period"] == per]
        cells.append({"institution_id": iid, "period": per, "n": len(group),
                      "mentions": sum(r["any_ai_cue"] for r in group)})
    return {"total_records": len(rows), "eligible_records": len(eligible),
            "unknown_degree": len(rows)-len(eligible), "institutions": institutions, "cells": cells,
            "period_counts": dict(Counter(r["period"] for r in eligible)),
            "claim": "Convenience pilot of metadata. No population prevalence, AI authorship or causal effects estimated."}
