"""Publication figures for all 225 metadata records and measured PDF coverage."""
from collections import Counter
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from synesis.corpus import load_metadata

INK, PAPER, TEAL, ORANGE = "#203936", "#f9f6ef", "#277e76", "#c26f46"
LABELS = {"uev": "Europea de Valencia", "upv": "UPV · València", "mit": "MIT · EE. UU.",
          "tu_berlin": "TU Berlin · Alemania", "hkust": "HKUST · Hong Kong", "usp": "USP · Brasil"}


def render(root=ROOT):
    metadata, _ = load_metadata(root)
    coverage = json.loads((root / "reports/fulltext_coverage.json").read_text())
    rows = {row["institution_id"]: row for row in coverage["institutions"]}
    order = ["uev", "upv", "mit", "tu_berlin", "hkust", "usp"]
    output = root / "assets/figures"
    plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": INK, "axes.labelcolor": INK,
                         "xtick.color": INK, "ytick.color": INK, "font.size": 11,
                         "svg.fonttype": "none", "svg.hashsalt": "synesis-0.2.0"})
    fig, ax = plt.subplots(figsize=(11, 5.7), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    y = np.arange(len(order))
    total = [rows[key]["metadata_records"] for key in order]
    available = [rows[key]["downloaded_records"] for key in order]
    ax.barh(y, total, color="#dedfd6", height=.56, label="Metadatos sin PDF recuperado")
    ax.barh(y, available, color=TEAL, height=.56, label="Trabajos con ≥1 PDF recuperado")
    for i, (count, denominator) in enumerate(zip(available, total)):
        ax.text(denominator + 1.4, i, f"{count}/{denominator}", va="center", fontsize=11, fontweight="bold")
    ax.set_yticks(y, [LABELS[key] for key in order])
    ax.invert_yaxis()
    ax.set_xlim(0, max(total) + 19)
    ax.set_xlabel("Trabajos; el número de archivos puede ser mayor por los anexos")
    ax.set_title("Synesis · del catálogo al documento", loc="left", fontsize=20, pad=38, fontweight="bold")
    ax.text(0, 1.045, f"225 registros · {coverage['downloaded_records']} con PDF · {coverage['pdf_files']} archivos originales", transform=ax.transAxes, fontsize=12)
    ax.legend(loc="lower right", frameon=False, fontsize=9)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=10)
    ax.grid(axis="x", alpha=.12)
    ax.set_axisbelow(True)
    fig.text(.04, .025, "Corte: 20/10/2026 · Fuentes: manifiestos institucionales · Cobertura de acceso, sin inferir uso de IA.", fontsize=9)
    fig.subplots_adjust(left=.25, right=.96, top=.78, bottom=.18)
    for suffix in ("png", "svg"):
        fig.savefig(output / f"coleccion_225.{suffix}", dpi=180, facecolor=PAPER, metadata={"Date": None} if suffix == "svg" else None)
    plt.close(fig)

    years = sorted({row["year"] for row in metadata if isinstance(row.get("year"), int)})
    counts = Counter((row["institution_id"], row.get("year")) for row in metadata)
    values = np.array([[counts[key, year] for year in years] for key in order])
    fig, ax = plt.subplots(figsize=(12, 4.7), facecolor=PAPER)
    cmap = LinearSegmentedColormap.from_list("synesis", ["#eeeae0", "#b8d1bf", TEAL])
    image = ax.imshow(values, cmap=cmap, aspect="auto", vmin=0)
    for i in range(len(order)):
        for j in range(len(years)):
            if values[i, j]:
                ax.text(j, i, str(values[i, j]), ha="center", va="center", fontsize=9,
                        color="white" if values[i, j] > values.max() * .55 else INK)
    ax.set_xticks(range(len(years)), [str(year) + ("*" if year == 2026 else "") for year in years], rotation=45, ha="right")
    ax.set_yticks(range(len(order)), [LABELS[key] for key in order])
    ax.tick_params(length=0, pad=8)
    ax.spines[:].set_visible(False)
    ax.set_title("Años declarados en los 225 metadatos", loc="left", fontsize=18, pad=21, fontweight="bold")
    fig.colorbar(image, ax=ax, fraction=.024, pad=.025, label="Registros")
    fig.text(.04, .035, "Muestra de conveniencia · Año de metadato ≠ defensa verificada · *2026 incompleto · Ausencia de filas ≠ ausencia de trabajos.", fontsize=9)
    fig.subplots_adjust(left=.23, right=.93, bottom=.26, top=.81)
    for suffix in ("png", "svg"):
        fig.savefig(output / f"cohortes_225.{suffix}", dpi=180, facecolor=PAPER, metadata={"Date": None} if suffix == "svg" else None)
    plt.close(fig)


if __name__ == "__main__":
    render()
