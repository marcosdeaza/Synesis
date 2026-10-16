#!/usr/bin/env python3
"""Build a new, bounded public distribution from the local Synesis audit.

Standard library only. This exports files locally; it never logs in, contacts a
service, creates a Git repository, or publishes anything remotely.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from urllib.parse import urlparse


COPY_TREES = ("src", "tests", "scripts", "docs", "config", "notebooks", ".github")
COPY_FILES = (
    "LICENSE", "LICENSE.md", "LICENSE.txt", "RIGHTS", "RIGHTS.md",
    "CONTRIBUTING", "CONTRIBUTING.md", "CITATION", "CITATION.cff", "CITATION.md",
    "pyproject.toml", "Makefile", ".gitignore", "assets/PROVENANCE.md",
)
EXCLUDED_NAMES = frozenset({
    ".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".cache", "cache", "caches", ".venv", "venv", "node_modules",
    "raw", "harvests", "private", "reports", "features", "figures",
    ".DS_Store", ".ipynb_checkpoints",
})
EXCLUDED_SUFFIXES = frozenset({
    ".pyc", ".pyo", ".log", ".png", ".jpg", ".jpeg", ".gif", ".webp",
    ".svg", ".pdf", ".tif", ".tiff", ".bmp", ".zip", ".tar", ".gz",
    ".mp4", ".mov", ".mp3", ".wav",
})
PUBLIC_FIELDS = (
    "id", "institution_id", "title", "abstract", "issued_raw", "year",
    "date_precision", "degree_level", "degree_evidence", "source_url",
    "record_identifier", "language", "subjects", "license", "retrieved_at",
    "evidence_kind", "campus", "campus_evidence_url", "abstract_available",
    "abstract_omitted_by_policy", "date_semantics", "date_evidence",
    "metadata_license", "metadata_license_evidence_url", "rights_statement",
    "rights_reference_url", "academic_date_verified",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def resolve_output(source: Path, requested: Path) -> Path:
    """Reject an existing destination, symlink, or destination inside source."""
    unresolved = Path(os.path.abspath(requested.expanduser()))
    if os.path.lexists(unresolved):
        raise ValueError(f"El destino ya existe; no se sobrescribe: {unresolved}")
    output = unresolved.resolve()
    if output == source or source in output.parents:
        raise ValueError("El destino debe estar fuera del repositorio de origen.")
    if output.exists():
        raise ValueError(f"El destino resuelto ya existe: {output}")
    return output


def select_public_rows(source: Path) -> tuple[list[dict], dict]:
    """Select only exact CC0 metadata with a concrete HTTP(S) evidence URL."""
    inputs = sorted((source / "data" / "pilot").glob("*.jsonl"))
    if not inputs:
        raise ValueError("No hay un inventario local en data/pilot/*.jsonl.")
    selected: list[dict] = []
    input_hashes = []
    local_counts: Counter = Counter()
    identifiers: set[str] = set()
    for path in inputs:
        if path.is_symlink():
            raise ValueError(f"No se leen datos a través de un enlace simbólico: {path.name}")
        payload = path.read_bytes()
        input_hashes.append({"path": str(path.relative_to(source)),
                             "sha256": sha256(payload), "bytes": len(payload)})
        for number, line in enumerate(payload.decode("utf-8").splitlines(), 1):
            if not line.strip():
                continue
            record = json.loads(line)
            if not isinstance(record, dict):
                raise ValueError(f"Fila no válida: {path.name}:{number}")
            local_counts[str(record.get("institution_id", "unknown"))] += 1
            evidence = record.get("metadata_license_evidence_url")
            if record.get("metadata_license") != "CC0-1.0":
                continue
            parsed = urlparse(evidence) if isinstance(evidence, str) else None
            if not parsed or parsed.scheme not in {"http", "https"} or not parsed.netloc:
                continue
            identifier = record.get("id")
            if not isinstance(identifier, str) or not identifier:
                raise ValueError(f"Registro seleccionado sin identificador: {path.name}:{number}")
            if identifier in identifiers:
                raise ValueError(f"Identificador seleccionado duplicado: {identifier}")
            identifiers.add(identifier)
            # Projection prevents new author, email, or original-text fields from
            # silently becoming public when the private/local schema expands.
            public = {key: record[key] for key in PUBLIC_FIELDS if key in record}
            public["abstract"] = None
            public["abstract_omitted_by_policy"] = True
            selected.append(public)
    if not selected:
        raise ValueError("No hay registros con metadata_license=CC0-1.0 y evidencia URL.")
    return selected, {
        "local_audit_records": sum(local_counts.values()),
        "local_audit_institutions": dict(sorted(local_counts.items())),
        "source_inputs": input_hashes,
    }


def copy_plan(source: Path) -> list[tuple[Path, Path]]:
    """Use an allowlist; never copy data/, reports/, .git, caches or plots."""
    plan: list[tuple[Path, Path]] = []
    for directory in COPY_TREES:
        tree = source / directory
        if tree.is_symlink():
            raise ValueError(f"Directorio de origen simbólico no permitido: {directory}")
        if not tree.is_dir():
            continue
        for current, directories, files in os.walk(tree, followlinks=False):
            parent = Path(current)
            directories[:] = sorted(name for name in directories
                                    if name not in EXCLUDED_NAMES
                                    and not (parent / name).is_symlink())
            for name in sorted(files):
                original = parent / name
                if (name in EXCLUDED_NAMES or original.is_symlink()
                        or original.suffix.lower() in EXCLUDED_SUFFIXES):
                    continue
                plan.append((original, original.relative_to(source)))
    for name in COPY_FILES:
        original = source / name
        if original.is_file() and not original.is_symlink():
            plan.append((original, Path(name)))
    banner = source / "assets" / "banner.png"
    if banner.is_file() and not banner.is_symlink():
        plan.append((banner, Path("assets/banner.png")))
    return plan


def copy_file(original: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if original.suffix.lower() == ".ipynb":
        # Notebook source is useful; embedded local results/figures are not.
        notebook = json.loads(original.read_text(encoding="utf-8"))
        for cell in notebook.get("cells", []):
            cell.pop("attachments", None)
            if cell.get("cell_type") == "code":
                cell["outputs"] = []
                cell["execution_count"] = None
        target.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
                          encoding="utf-8")
    else:
        shutil.copy2(original, target)


def public_readme(local_count: int, selected_count: int) -> str:
    return f'''<p align="right"><strong>ES</strong> · <a href="README.en.md">EN</a></p>

![Synesis · Tierra](assets/banner.png)

# Synesis

Investigación reproducible sobre TFG, TFM y equivalentes universitarios alrededor de la difusión de la IA generativa. El foco es Valencia; la **Universidad Europea de Valencia es obligatoria** en el diseño, junto a UPV y comparadores nacionales e internacionales.

Esta es la **distribución pública minimizada**: la auditoría local de origen examinó **{local_count} registros reales**; aquí se distribuyen **{selected_count} registros de metadatos con CC0-1.0 y evidencia verificable**, actualmente de TU Berlin. Son una muestra de conveniencia para probar procedencia y reproducción, sin estimaciones de adopción ni efectos causales.

UEV está presente en el registro institucional, el protocolo y el estudio local. **Sus registros no se redistribuyen todavía**: sus permisos de publicación de metadatos requieren revisión. Lo mismo ocurre con los demás registros excluidos. Los documentos de auditoría describen históricamente la muestra local; los informes de `reports/` se recalculan exclusivamente con las {selected_count} filas distribuidas. Consulta el [alcance de esta variante](docs/PUBLICACION.md).

## Leer y continuar

- [Protocolo científico](docs/PROTOCOLO.md) y [plan de análisis](docs/PLAN_ANALISIS.md).
- [Fuentes y permisos](docs/FUENTES.md), [auditoría de España](docs/FUENTES_ESPANA.md) y [auditoría internacional](docs/FUENTES_GLOBALES.md).
- [Continuidad de la versión pública](CONTEXTO_PUBLICO.md) y [cronología](docs/CRONOLOGIA.md).
- [Informe reproducido de esta distribución](reports/PILOTO.md) y [derechos por capa](RIGHTS.md).

La memoria completa local no se copia. `CONTEXTO.md` en esta variante enlaza a la continuidad pública documentada arriba.

![Composición del subconjunto público](assets/figures/corpus.png)

![Cobertura del subconjunto público por año de metadatos](assets/figures/cobertura_temporal.png)

## Reproducir sin red

Python 3.11 o posterior; el pipeline y las pruebas usan únicamente la biblioteca estándar:

```sh
make reproduce
```

Entrada: `data/pilot/rights_cleared.jsonl`. Salidas: `reports/`, reconstruidas localmente. Los fixtures sintéticos de las pruebas comprueban el software; nunca forman parte del corpus de investigación. Las figuras originales de la auditoría local no se incluyen. Pueden regenerarse para este subconjunto con el extra opcional de figuras, tras revisar sus rótulos y denominadores.

Una mención de IA no acredita uso. Un año de repositorio no prueba defensa. CC0 se refiere a los **metadatos seleccionados**: no autoriza a redistribuir las tesis o PDF ni implica permiso de entrenamiento sobre esas obras.

No se ha creado un repositorio remoto ni elegido visibilidad. La última comprobación de autenticación de GitHub encontró una credencial inválida; la publicación remota sigue pendiente.
'''


def public_context(audit: dict, selected: list[dict]) -> str:
    counts = dict(sorted(Counter(row["institution_id"] for row in selected).items()))
    return f'''# Synesis · continuidad pública

Esta variante parte de una auditoría local de {audit["local_audit_records"]} registros reales. Distribuye {len(selected)} filas cuya licencia de metadatos es exactamente `CC0-1.0` y cuya evidencia de licencia tiene URL verificable. Recuento público: `{json.dumps(counts, ensure_ascii=False)}`.

La memoria operativa completa del origen se denomina `CONTEXTO.md`; deliberadamente no se incluye en esta distribución. Este archivo conserva el contexto necesario para continuar con los materiales públicos, sin afirmar acceso al inventario local completo.

## Decisiones que deben mantenerse

- Español principal. Universidad Europea de Valencia obligatoria en el diseño; UEV y UPV prioritarias para el trabajo de campo local. Su ausencia del dataset público actual es una decisión de redistribución, no una exclusión de la investigación.
- Metadatos, tesis, código y documentación tienen derechos distintos. CC0 de los metadatos seleccionados no se extiende a las obras ni a corpus de entrenamiento. Cada nueva fuente requiere evidencia y revisión por operación.
- No inferir uso de IA por estilo, detectores, fecha o menciones temáticas. No atribuir cambios a IA solo por proximidad temporal.
- No confundir emisión en repositorio, defensa, redacción o depósito. El subconjunto TU Berlin no tiene fecha académica confirmada y procede de trabajos seleccionados por nota y aval; no representa la producción total.
- Las auditorías históricas de `docs/FUENTES_*` describen el inventario local. `reports/` y `data/pilot/rights_cleared.jsonl` describen exclusivamente esta variante pública.
- No incorporar datos de prueba al corpus; mantener autores, correos, abstracts y PDF fuera de la distribución actual.

## Cómo retomar

1. Leer `README.md`, `docs/PUBLICACION.md`, el protocolo y las fuentes.
2. Ejecutar `make reproduce`, sin red ni credenciales. Revisar el manifiesto y las incidencias.
3. Para ampliar, registrar licencia de metadatos, evidencia, condiciones técnicas, operación permitida y semántica de fechas antes de extraer o publicar datos.
4. Cambiar gráficos y denominadores según el corpus efectivamente distribuido. No reutilizar figuras del inventario local como si fueran resultados públicos.
5. Registrar cada decisión nueva en este archivo y mantener protocolo, diccionario, permisos y pruebas consistentes.

Pendientes: cerrar permisos del núcleo valenciano, auditar fechas académicas, balancear cohortes/disciplinas, anotar evidencia humana y prerregistrar antes de análisis confirmatorio. No se han entrenado modelos con estos trabajos. GitHub sigue pendiente de autenticación válida y elección de visibilidad; este exportador no realiza publicación remota.
'''


def export(source: Path, requested: Path) -> dict:
    output = resolve_output(source, requested)
    if (source / "PUBLIC_EXPORT_MANIFEST.json").exists():
        raise ValueError("Esta ya es una variante pública. Reproduce sus informes con make reproduce; exporta desde la auditoría local principal.")
    selected, audit = select_public_rows(source)
    plan = copy_plan(source)
    # Atomic creation refuses a destination that appears between validation and
    # copying. Never merge with or overwrite a pre-existing directory.
    output.mkdir(parents=True, exist_ok=False)
    try:
        for original, relative in plan:
            copy_file(original, output / relative)
        dataset = output / "data/pilot/rights_cleared.jsonl"
        dataset.parent.mkdir(parents=True, exist_ok=True)
        dataset.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n"
                                   for row in selected), encoding="utf-8")
        (output / "README.md").write_text(public_readme(audit["local_audit_records"], len(selected)), encoding="utf-8")
        (output / "CONTEXTO_PUBLICO.md").write_text(public_context(audit, selected), encoding="utf-8")
        (output / "CONTEXTO.md").write_text("# Continuidad de Synesis público\n\nLee [CONTEXTO_PUBLICO.md](CONTEXTO_PUBLICO.md) y actualízalo al cerrar cada hito. La memoria local completa de la auditoría no se incluye en esta variante.\n", encoding="utf-8")
        (output / "AGENTS.md").write_text("# Continuar Synesis público\n\nLee CONTEXTO_PUBLICO.md al comenzar. Actualízalo con cada decisión y al cerrar la sesión. Ejecuta make reproduce. No presupongas acceso al inventario local de 225 registros ni publiques materiales nuevos sin revisar sus derechos.\n", encoding="utf-8")
        (output / "README.en.md").write_text(f'''<p align="right"><a href="README.md">ES</a> · <strong>EN</strong></p>

![Synesis](assets/banner.png)

# Synesis

Reproducible research on university capstone and master's theses across the generative AI transition. Spanish is the primary language. Universidad Europea de Valencia is mandatory in the design.

The source audit examined {audit["local_audit_records"]} real records locally. This public variant distributes only {len(selected)} metadata records with explicit CC0 evidence, currently from TU Berlin. These metadata rights do not extend to thesis PDFs. UEV remains in the protocol and institutional registry; its records are not redistributed yet.

This is a convenience pilot, not an estimate of AI use or causal effects. Repository dates do not automatically mean defense dates. No full text, abstracts, author fields, human labels or trained model weights are distributed.

Read the [protocol](docs/PROTOCOLO.md), [source audit](docs/FUENTES.md), [public continuity](CONTEXTO_PUBLICO.md) and [current pilot report](reports/PILOTO.md). Run `make reproduce` with Python 3.11+ to rebuild offline. See [publication scope](docs/PUBLICACION.md).
''', encoding="utf-8")
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(output / "src")
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        result = subprocess.run(
            [sys.executable, "-m", "synesis.cli", "--root", str(output), "build"],
            cwd=output, env=environment, capture_output=True, text=True, check=False,
        )
        if result.returncode:
            raise RuntimeError("La reconstrucción offline falló: " + (result.stderr.strip() or result.stdout.strip())[-2000:])
        report = json.loads((output / "reports/manifest.json").read_text(encoding="utf-8"))
        if report.get("records_in") != len(selected) or report.get("records_out") != len(selected):
            raise RuntimeError("El informe reconstruido no conserva exactamente las filas autorizadas.")
        manifest = {
            "variant": "public_metadata_cc0", "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            **audit, "distributed_records": len(selected),
            "distributed_institutions": dict(sorted(Counter(row["institution_id"] for row in selected).items())),
            "selection": "metadata_license exactly CC0-1.0 AND nonempty HTTP(S) metadata_license_evidence_url",
            "dataset": {"path": "data/pilot/rights_cleared.jsonl", "sha256": sha256(dataset.read_bytes())},
            "license_scope": "CC0 covers selected metadata only; no license for theses, PDFs or model training is inferred.",
            "exclusions": ["original pilot datasets", "raw", "harvests", "caches", ".git", "original reports/features", "original plots", "original local CONTEXTO.md; public index substituted"],
            "notebooks": "code outputs, execution counts and attachments removed",
            "offline_build": "python -m synesis.cli --root <export> build; succeeded",
            "remote_publication": "not performed; authentication and visibility pending",
        }
        (output / "PUBLIC_EXPORT_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except Exception as error:
        raise RuntimeError(f"Exportación incompleta conservada para inspección en {output}: {error}") from error
    return {"output": str(output), "local_audit_records": audit["local_audit_records"],
            "distributed_records": len(selected), "dataset_sha256": manifest["dataset"]["sha256"]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Exporta una variante pública local con metadatos CC0 verificados; no publica en GitHub.")
    parser.add_argument("--output", type=Path, required=True,
                        help="Ruta nueva fuera del repositorio de origen; nunca se sobrescribe.")
    arguments = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    try:
        result = export(source, arguments.output)
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, f"Error: {error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
