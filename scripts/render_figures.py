"""Publication-friendly descriptive plots; no inferred adoption rates."""
from pathlib import Path
import csv
import json
import os

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT/".cache/matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = ROOT/"assets/figures"
OUT.mkdir(parents=True, exist_ok=True)
ROWS = [json.loads(s) for s in (ROOT/"reports/features.jsonl").read_text(encoding="utf-8").splitlines() if s]
SUMMARY = json.loads((ROOT/"reports/summary.json").read_text(encoding="utf-8"))
NAMES = {"uev": "Europea de Valencia", "upv": "UPV · RiuNet", "mit": "MIT · EE. UU.",
         "usp": "USP · Brasil", "tu_berlin": "TU Berlin · Alemania", "hkust": "HKUST · Hong Kong"}
ORDER = [s for s in ["uev", "upv", "mit", "usp", "tu_berlin", "hkust"] if any(r["institution_id"] == s for r in ROWS)]
BG, INK, MUTED, TERRA, BLUE = "#f7f3e9", "#202523", "#59615d", "#af5b35", "#2b566b"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "text.color": INK,
    "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": INK, "axes.edgecolor": "#d4d4c9",
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "svg.fonttype": "none", "axes.spines.top": False, "axes.spines.right": False})


def save(fig, name):
    for ext in ["png", "svg", "pdf"]:
        fig.savefig(OUT/f"{name}.{ext}", dpi=180, bbox_inches="tight")
    plt.close(fig)


fig, ax = plt.subplots(figsize=(12, max(3.6, len(ORDER)*.75+1.5)))
stats = {r["institution_id"]: r for r in SUMMARY["institutions"]}
y = np.arange(len(ORDER))
bachelor = [sum(r["degree_level"] == "bachelor" for r in ROWS if r["institution_id"] == s) for s in ORDER]
master = [sum(r["degree_level"] == "master" for r in ROWS if r["institution_id"] == s) for s in ORDER]
ax.barh(y, bachelor, color=BLUE, label="Grado / bachelor")
ax.barh(y, master, left=bachelor, color=TERRA, label="Máster / master", hatch="///")
for index, iid in enumerate(ORDER):
    offset = max(.15, max(r["eligible"] for r in stats.values())*.015)
    ax.text(stats[iid]["eligible"]+offset, index, str(stats[iid]["eligible"]), va="center", weight="bold")
ax.set_yticks(y, [NAMES[s] for s in ORDER])
ax.invert_yaxis()
if len(ORDER) == 1:
    ax.set_ylim(.95, -.95)
ax.set_xlim(0, max(r["eligible"] for r in stats.values())*1.15)
ax.set_xlabel("Número de registros en este piloto")
ax.set_title("Synesis / El corpus inicial, fuente por fuente", loc="left", pad=42, fontsize=19, fontfamily="DejaVu Serif")
ax.text(0, 1.04, f"{len(ROWS)} registros reales · selección de conveniencia · corte 16 oct 2026", transform=ax.transAxes, color=MUTED)
ax.legend(frameon=False, loc="lower right")
ax.spines["left"].set_visible(False)
fig.text(.02, -.015, "Los tamaños reflejan la extracción piloto; no la producción ni la adopción de IA de cada universidad.", fontsize=10, color=MUTED)
fig.tight_layout()
save(fig, "corpus")


years = list(range(min(r["year"] for r in ROWS if r["year"] is not None), max(r["year"] for r in ROWS if r["year"] is not None)+1))
matrix = np.array([[sum(r["institution_id"] == iid and r["year"] == year for r in ROWS) for year in years] for iid in ORDER])
fig, ax = plt.subplots(figsize=(14, max(3.2, len(ORDER)*.6+2.2)))
from matplotlib.colors import LinearSegmentedColormap
cmap = LinearSegmentedColormap.from_list("synesis", ["#eeeadd", "#7e9da4", BLUE])
heat = ax.imshow(matrix, cmap=cmap, aspect="auto", vmin=0)
for i in range(len(ORDER)):
    for j in range(len(years)):
        val = int(matrix[i, j])
        ax.text(j, i, str(val) if val else "—", ha="center", va="center", fontsize=10,
                color="white" if val > matrix.max()*.55 else INK)
ax.set_yticks(range(len(ORDER)), [NAMES[s] for s in ORDER])
ax.set_xticks(range(len(years)), years, rotation=45, ha="right")
ax.set_title("Cobertura temporal del piloto", loc="left", pad=44, fontsize=19, fontfamily="DejaVu Serif")
ax.text(0, 1.07, "Conteos por año del metadato o listado de origen; las fechas de defensa no están armonizadas", transform=ax.transAxes, color=MUTED)
ax.set_xlabel("Año declarado en la fuente · 2026 incompleto")
colorbar = fig.colorbar(heat, ax=ax, label="Registros", shrink=.75, pad=.02)
from matplotlib.ticker import MaxNLocator
colorbar.locator = MaxNLocator(integer=True)
colorbar.update_ticks()
missing = sum(r["year"] is None for r in ROWS)
date_note = " UPV: issued suele coincidir con ingreso." if "upv" in ORDER else " Fecha académica pendiente de verificar."
fig.text(.02, -.02, f"— = ningún registro en este piloto, no ausencia de trabajos. {missing} registros sin año no se muestran."+date_note, color=MUTED, fontsize=10)
fig.tight_layout()
save(fig, "cobertura_temporal")


upv = [r for r in ROWS if r["institution_id"] == "upv"]
if upv:
    same_day = sum(bool(r.get("issued_raw") and r.get("accessioned_raw")) and r["issued_raw"][:10] == r["accessioned_raw"][:10] for r in upv)
    with_created = sum(bool(r.get("created_raw")) for r in upv)
    fig, ax = plt.subplots(figsize=(10, 3.8))
    ax.barh([0], [same_day], color=TERRA, label="issued coincide con accessioned (día)")
    ax.barh([0], [len(upv)-same_day], left=[same_day], color=BLUE, label="No coincide / sin dato")
    ax.set_xlim(0, len(upv)); ax.set_yticks([])
    ax.set_xlabel(f"Registros UPV revisados (n={len(upv)})")
    ax.set_title("La fecha cambia la pregunta", loc="left", fontsize=19, pad=42, fontfamily="DejaVu Serif")
    ax.text(0, 1.08, f"{same_day}/{len(upv)} fechas issued coinciden con el ingreso al repositorio", transform=ax.transAxes, color=MUTED)
    ax.text(same_day/2, 0, str(same_day), color="white", ha="center", va="center", weight="bold", fontsize=18)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(.5, -.27), ncol=1)
    fig.text(.02, -.16, f"No acredita fecha de defensa. created_raw está disponible en {with_created}/{len(upv)} registros y requiere validar su significado.", color=MUTED, fontsize=10)
    fig.tight_layout()
    save(fig, "auditoria_fechas")


timeline = ROOT/"config/ai_milestones.csv"
if timeline.exists():
    events = list(csv.DictReader(timeline.open(encoding="utf-8")))
    if events:
        fig, ax = plt.subplots(figsize=(13, max(6, len(events)*.48)))
        yy = np.arange(len(events))
        ax.scatter([0]*len(events), yy, color=TERRA, s=38, zorder=3)
        ax.plot([0, 0], [0, len(events)-1], color="#c9cabc", linewidth=1, zorder=1)
        for i, event in enumerate(events):
            ax.text(-.06, i, event["date"], ha="right", va="center", color=MUTED, fontsize=10)
            label = event["label"]
            ax.text(.06, i, label, va="center", fontsize=11)
        ax.set_xlim(-.24, 1.3); ax.set_ylim(len(events)-.3, -.7)
        ax.axis("off")
        ax.set_title("Hitos de disponibilidad de la IA generativa", loc="left", fontsize=19, pad=25, fontfamily="DejaVu Serif")
        fig.text(.06, .015, "Disponibilidad ≠ adopción. Fuentes primarias y contexto en config/ai_milestones.csv · Corte 16 oct 2026", fontsize=10, color=MUTED)
        fig.tight_layout(rect=[0,.05,1,1])
        save(fig, "cronologia")

print("Figures exported to", OUT)
