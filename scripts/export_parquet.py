"""Stream corpus JSONL into typed Parquet tables; third-party rights are preserved."""
import argparse
import json
from pathlib import Path


def export(folder: Path) -> dict:
    import pyarrow as pa
    import pyarrow.parquet as pq
    specs = {
        "catalog": [("record_id", pa.string()), ("institution_id", pa.string()), ("title", pa.string()),
                    ("year", pa.int64()), ("degree_level", pa.string()), ("language", pa.string()),
                    ("source_url", pa.string()), ("fulltext_status", pa.string()), ("work_group_id", pa.string())],
        "documents": [("document_id", pa.string()), ("record_id", pa.string()), ("work_group_id", pa.string()),
                      ("pdf_sha256", pa.string()), ("path", pa.string()), ("status", pa.string()),
                      ("page_count", pa.int64()), ("text_page_count", pa.int64()), ("source_license", pa.string())],
        "pages": [("page_id", pa.string()), ("document_id", pa.string()), ("record_id", pa.string()),
                  ("page_number", pa.int64()), ("text", pa.string()), ("text_sha256", pa.string()),
                  ("status", pa.string()), ("source_url", pa.string()), ("source_license", pa.string())],
        "chunks": [("chunk_id", pa.string()), ("record_id", pa.string()), ("work_group_id", pa.string()),
                   ("document_id", pa.string()), ("page_id", pa.string()), ("page_number", pa.int64()),
                   ("start_char", pa.int64()), ("end_char", pa.int64()), ("text", pa.string()),
                   ("pdf_sha256", pa.string()), ("text_sha256", pa.string()), ("source_url", pa.string()),
                   ("source_license", pa.string())],
    }
    counts = {}
    for name, fields in specs.items():
        schema = pa.schema(fields + [("record_json", pa.string())], metadata={
            b"synesis_schema_version": b"0.2.0",
            b"rights": b"Per-source terms apply; no blanket license. record_json preserves all JSONL fields.",
            b"offsets": b"Unicode code points in normalized page text; [start,end)."})
        temporary = folder / (name + ".parquet.part")
        count = 0
        try:
            with pq.ParquetWriter(temporary, schema, compression="zstd") as writer:
                batch = []
                with (folder / (name + ".jsonl")).open(encoding="utf-8") as stream:
                    for line in stream:
                        if not line.strip():
                            continue
                        row = json.loads(line)
                        searchable = {**row.get("metadata", {}), **row} if name == "catalog" else row
                        value = {key: searchable.get(key) for key, _ in fields}
                        value["record_json"] = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                        batch.append(value)
                        if len(batch) == 1000:
                            writer.write_table(pa.Table.from_pylist(batch, schema=schema))
                            count += len(batch)
                            batch = []
                    if batch:
                        writer.write_table(pa.Table.from_pylist(batch, schema=schema))
                        count += len(batch)
            temporary.replace(folder / (name + ".parquet"))
            counts[name] = count
        finally:
            temporary.unlink(missing_ok=True)
    return counts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, default=Path(__file__).resolve().parents[1] / "data/derived")
    print(json.dumps(export(parser.parse_args().folder), indent=2))
