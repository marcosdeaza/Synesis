<p align="right"><strong>ES</strong> · <a href="README.en.md">EN</a></p>

![Synesis · Tierra](assets/banner.png)

# Synesis

**v0.1.0 · 225 registros reales publicados · [Repositorio público](https://github.com/marcosdeaza/Synesis)**

Investigación reproducible sobre TFG, TFM y equivalentes universitarios alrededor de la difusión de la IA generativa. El foco es Valencia; la **Universidad Europea de Valencia es obligatoria** en el diseño, junto a UPV y comparadores nacionales e internacionales.

Esta distribución publica los **225 registros reales de metadatos de seis fuentes** reunidos en la auditoría inicial de 13 instituciones. La colección está en [`data/research_225/`](data/research_225/): UEV (90), UPV (100), MIT (10), TU Berlin (10), HKUST (10) y USP (5). Es una muestra de conveniencia para investigar fuentes, cobertura y métodos; no estima adopción de IA ni efectos causales.

Los 225 metadatos se publican con el permiso confirmado por el responsable, registrado en [`PERMISSIONS.json`](data/research_225/PERMISSIONS.json), manteniendo las licencias de origen. No se incluyen PDFs, texto completo, resúmenes ni campos de autoría/contacto, y no se ha entrenado un modelo con estos trabajos.

| Colección | Registros | Función |
|---|---:|---|
| [`research_225`](data/research_225/) | **225 únicos** | Metadatos publicados según el permiso confirmado por el responsable; archivos de España y comparadores internacionales, procedencia y manifiesto |
| [`pilot/rights_cleared.jsonl`](data/pilot/rights_cleared.jsonl) | **10 de TU Berlin** | Subconjunto con evidencia institucional CC0-1.0 que utiliza el pipeline reproducible |

Los 10 registros del piloto **ya están incluidos entre los 225**: no hay 235 trabajos únicos. Los informes analíticos y las figuras de esta versión se calculan exclusivamente con el piloto de 10; la validación de los 225 tiene un informe separado. [Alcance y publicación](docs/PUBLICACION.md) · [Ficha de los datos](docs/DATASET_CARD.md).

## Qué estudia Synesis

Dos líneas separadas: cambios observables en temas, métodos y referencias, y evidencia explícita de uso declarado de IA. Las fechas de lanzamiento describen disponibilidad tecnológica; su relación con las prácticas académicas debe investigarse con cobertura, fechas y anotación verificadas.

## Leer y continuar

- [Protocolo científico](docs/PROTOCOLO.md) y [plan de análisis](docs/PLAN_ANALISIS.md).
- [Fuentes y permisos](docs/FUENTES.md), [auditoría de España](docs/FUENTES_ESPANA.md) y [auditoría internacional](docs/FUENTES_GLOBALES.md).
- [Continuidad de la versión pública](CONTEXTO_PUBLICO.md) y [cronología](docs/CRONOLOGIA.md).
- [Informe reproducido de esta distribución](reports/PILOTO.md) y [derechos por capa](RIGHTS.md).

La memoria completa local no se copia. `CONTEXTO.md` en esta variante enlaza a la continuidad pública documentada arriba.

![Composición del piloto reproducible de 10 registros CC0](assets/figures/corpus.png)

![Cobertura del piloto de 10 registros por año de metadatos](assets/figures/cobertura_temporal.png)

## Hitos y pipeline

![Hitos de disponibilidad tecnológica con fuentes primarias](assets/figures/cronologia.png)

```mermaid
flowchart LR
  A[Fuentes universitarias] --> B[Permisos y cobertura]
  B --> C[Cosecha acotada]
  C --> D[Snapshot y SHA-256]
  D --> E[Validación y fechas]
  E --> F[Anotación de evidencia]
  F --> G[Análisis y figuras]
```

## Reproducir sin red

Python 3.11 o posterior; el pipeline y las pruebas usan únicamente la biblioteca estándar:

```sh
make reproduce
```

`make reproduce` valida los **225 registros completos** mediante `scripts/check_research_snapshot.py` y reconstruye por separado el análisis del piloto de **10 registros** de `data/pilot/rights_cleared.jsonl`. Los resultados se guardan en `reports/`; [`research_225_validation.json`](reports/research_225_validation.json) corresponde a la validación de los 225 y [`manifest.json`](reports/manifest.json) a las diez entradas del análisis. La colección completa tiene su propio [manifiesto](data/research_225/manifest.json). Los fixtures sintéticos de las pruebas comprueban el software y no forman parte del corpus de investigación. Las figuras analíticas usan exclusivamente el piloto de 10; se regeneran instalando el extra opcional `.[figures]` y ejecutando `make figures`.

Una mención de IA no acredita uso. Un año de repositorio no prueba defensa. La evidencia CC0 del piloto de 10 se refiere a esos metadatos; el permiso declarado para la colección de 225 tiene su propio registro y alcance. Ninguno se extiende aquí a redistribuir tesis, PDFs o materiales ausentes del paquete.

Preparación inicial de código y documentación asistida por IA; revisión académica independiente pendiente. No se presentan resultados causales ni estimaciones de adopción. [Cómo contribuir](CONTRIBUTING.md) · [Bibliografía](docs/BIBLIOGRAFIA.bib).
