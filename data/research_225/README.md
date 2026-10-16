# Synesis · 225 registros reales

Snapshot completo de metadatos de la investigación, publicado por instrucción del responsable del proyecto, que confirma disponer de permiso para publicarlo y para su uso investigativo y eventual entrenamiento. La declaración y su alcance están registrados en [PERMISSIONS.json](PERMISSIONS.json); las licencias observadas de cada fuente se conservan sin modificarlas.

| Archivo | Registros | Instituciones |
|---|---:|---|
| [spain.jsonl](spain.jsonl) | 190 | UEV: 90; UPV: 100 |
| [global.jsonl](global.jsonl) | 35 | MIT: 10; TU Berlin: 10; HKUST: 10; USP: 5 |
| **Total único** | **225** | Seis instituciones |

Cada línea JSONL representa un trabajo referenciado. Son metadatos: título, materias, nivel, fechas de la fuente, derechos observados y enlaces de procedencia. No incluye los textos completos, PDFs, resúmenes, campos de autores ni correos. Los enlaces públicos pueden identificar autores en origen; la minimización no es anonimización.

Los diez registros de [la muestra CC0](../pilot/rights_cleared.jsonl) ya están dentro de estos 225. No concatenar ambas colecciones para contar trabajos: la unión sigue siendo 225.

## Cargar el conjunto completo

Desde la raíz del repositorio, con Python y su biblioteca estándar:

```python
from pathlib import Path
import json

folder = Path("data/research_225")
records = [
    json.loads(line)
    for name in ("spain.jsonl", "global.jsonl")
    for line in (folder / name).read_text(encoding="utf-8").splitlines()
    if line.strip()
]
assert len(records) == len({row["id"] for row in records}) == 225
```

[manifest.json](manifest.json) conserva recuentos y SHA-256 por archivo. `make reproduce` valida esta carpeta, además de reproducir por separado el piloto CC0 de diez registros.

## Uso en futuros modelos

Este snapshot sirve como base de investigación sobre metadatos. No contiene etiquetas humanas finalizadas ni modelos entrenados. Una mención de IA no demuestra que el trabajo se redactase con IA; el año del repositorio tampoco demuestra fecha de defensa. Para un experimento supervisado habrá que definir la tarea, anotar y separar entrenamiento, validación y prueba por obra, siguiendo la [ficha de modelos](../../docs/MODEL_CARD.md) y el [plan de análisis](../../docs/PLAN_ANALISIS.md).

La confirmación del responsable se registra como tal; no se presenta como una licencia CC0 general ni como una autorización institucional comprobada de forma independiente. La licencia del código de Synesis no se extiende a estos metadatos de terceros.
