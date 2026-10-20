from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from .core import curate, read_jsonl, summary


def build(root: Path) -> dict:
    files = sorted((root/"data/pilot").glob("*.jsonl"))
    if not files:
        raise ValueError("No real pilot files found in data/pilot.")
    rows, issues = curate([r for path in files for r in read_jsonl(path)])
    report = root/"reports"
    report.mkdir(exist_ok=True)
    stats = summary(rows)
    sources = []
    for path in sorted((root/"config").glob("institutions_*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        sources.extend(value if isinstance(value, list) else value.get("institutions", []))
    known = {s["id"] for s in sources}
    for r in rows:
        if r["institution_id"] not in known:
            issues.append({"id": r["id"], "issues": ["institution_not_in_registry"]})
    manifest = {"release": "0.2.0", "snapshot_date": "2026-10-16", "sampling": "convenience/source audit; NOT representative",
        "inputs": [{"path": str(path.relative_to(root)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "bytes": path.stat().st_size} for path in files],
        "records_in": sum(len(read_jsonl(path)) for path in files), "records_out": len(rows),
        "issue_count": len(issues), "code_version": "0.2.0", "analysis": "title + available subjects; abstracts not redistributed",
        "privacy": "No author/supervisor fields; source pages may identify authors.",
        "license": "Third-party metadata: per source; no blanket license or training permission."}
    (report/"manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    (report/"quality.json").write_text(json.dumps(issues, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    (report/"summary.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    (report/"features.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False)+"\n" for r in rows), encoding="utf-8")
    with (report/"coverage.csv").open("w", encoding="utf-8", newline="") as stream:
        fields = ["institution_id", "records", "eligible", "abstracts", "abstracts_analyzed", "cue_mentions", "min_year", "max_year"]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(stats["institutions"])
    lines = ["# Auditoría del piloto real", "", "Corte: 16 de octubre de 2026. Muestra de conveniencia; no representa el conjunto de trabajos de ninguna universidad.", "",
             f"Registros: **{stats['total_records']}**; nivel grado/máster identificable: **{stats['eligible_records']}**; incidencias de validación: **{len(issues)}**.", "",
             "| Institución | Registros | Grado/máster | Años en metadatos | Resúmenes en origen | Resúmenes analizados | Menciones léxicas |",
             "|---|---:|---:|---|---:|---:|---:|"]
    for item in stats["institutions"]:
        lines.append(f"| {item['institution_id']} | {item['records']} | {item['eligible']} | {item['min_year']}–{item['max_year']} | {item['abstracts']} | {item['abstracts_analyzed']} | {item['cue_mentions']} |")
    lines += ["", "Las menciones se buscan en el título y las materias disponibles. No acreditan uso de IA, autoría, calidad ni integridad académica. Los resúmenes no redistribuidos no se analizan. El año procede del metadato o listado de origen y no demuestra la fecha de defensa o redacción.", "",
              "No calculamos una diferencia antes/después: la selección y los denominadores todavía no lo permiten. 2026 es un año incompleto. El inventario y la cronología son los resultados de esta versión; las hipótesis siguen abiertas.", "",
              "## Reproducción", "", "Los hashes SHA-256 de cada entrada están en `manifest.json`. `coverage.csv` contiene los valores de las figuras; `quality.json` lista rechazos y problemas. `features.jsonl` añade señales calculadas sin sustituir los campos originales.", ""]
    (report/"PILOTO.md").write_text("\n".join(lines), encoding="utf-8")
    return {"manifest": manifest, "summary": stats}


def main() -> None:
    parser = argparse.ArgumentParser(description="Synesis research pipeline")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build", help="Validate, deduplicate and summarize the shipped real pilot offline")
    sub.add_parser("check", help="Validate pilot and fail on any issue")
    hp = sub.add_parser("harvest", help="Bounded OAI harvest to ignored local storage; never fetches PDFs")
    hp.add_argument("--institution", required=True)
    hp.add_argument("--set", dest="set_spec", required=True)
    hp.add_argument("--contact", required=True, help="Your public project URL or contact email for the user agent")
    hp.add_argument("--output", required=True, type=Path)
    hp.add_argument("--pages", type=int, default=1)
    hp.add_argument("--metadata-prefix", choices=["oai_dc", "dim"], default="oai_dc")
    hp.add_argument("--since")
    hp.add_argument("--until")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.command in {"build", "check"}:
        output = build(root)
        print(json.dumps(output["manifest"], ensure_ascii=False, indent=2))
        if output["manifest"]["issue_count"]:
            raise SystemExit(1)
    else:
        from .harvest import harvest
        sources = []
        for path in (root/"config").glob("institutions_*.json"):
            value = json.loads(path.read_text(encoding="utf-8"))
            sources.extend(value if isinstance(value, list) else value.get("institutions", []))
        matches = [s for s in sources if s["id"] == args.institution]
        if len(matches) != 1 or not matches[0].get("oai_base"):
            raise SystemExit("Source needs a verified OAI endpoint in config/institutions_*.json.")
        target = args.output.resolve()
        storage = (root/"data/harvests").resolve()
        if storage not in target.parents:
            raise SystemExit("Harvest output must be inside ignored data/harvests/, in a new snapshot directory.")
        print(json.dumps(harvest(matches[0]["oai_base"], args.institution, args.set_spec,
            target, args.contact, args.pages, args.since, args.until,
            metadata_prefix=args.metadata_prefix), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
