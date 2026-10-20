<p align="right"><a href="README.md">ES</a> · <strong>EN</strong></p>

![Synesis](assets/banner.png)

# Synesis

Reproducible research on university capstone and master's theses across the generative AI transition. Spanish is the primary language. Universidad Europea de Valencia is mandatory in the design.

This repository publishes **225 real metadata records from six sources**, following an audit of 13 institutions: Universidad Europea de Valencia (90), UPV (100), MIT (10), TU Berlin (10), HKUST (10) and USP (5). Download the complete collection from [`data/research_225/`](data/research_225/), with its [manifest](data/research_225/manifest.json).

The 225 metadata records are published with permission confirmed by the project owner, recorded in [`PERMISSIONS.json`](data/research_225/PERMISSIONS.json), while preserving source licenses.

A separate **10-record CC0 pilot from TU Berlin**, [`data/pilot/rights_cleared.jsonl`](data/pilot/rights_cleared.jsonl), drives the analytical pipeline, reports and figures. These 10 records are already included in the 225: there are **225 unique works, not 235**.

Both collections come from convenience sampling and do not estimate AI adoption or causal effects. Repository dates do not automatically mean defense dates. The metadata snapshot has no abstracts or author/contact fields; no completed human labels or trained model weights are distributed. No model has been trained on these works.

## Full text and reusable datasets (v0.2)

![PDF coverage by institution](assets/figures/coleccion_225.png)

Of the 225 records, **158 have at least one original PDF** (225 files, 2.41 GB): UEV 86/90, UPV 47/100 (114 files including annexes), MIT 10/10, TU Berlin 10/10, USP 5/5, HKUST 0/10 (the repository's `robots.txt` forbids automated access; it is not circumvented). Every one of the 225 has a documented status. A local corpus is built on top: **13,558 pages, 20,204 chunks** (never crossing a page or work), SQLite FTS5 and Parquet, each chunk carrying page, offsets, PDF SHA-256, source URL and observed license. 153 documents have extracted text, 40 partial text and 32 would need OCR (not run).

PDFs and derivatives live in the [v0.2.0 release](https://github.com/marcosdeaza/Synesis/releases/tag/v0.2.0), not in Git history:

```sh
python3 scripts/download_release.py --tag v0.2.0           # metadata + processed corpus
python3 scripts/download_release.py --tag v0.2.0 --pdfs    # adds original PDFs
python3 scripts/search_corpus.py 'artificial intelligence' --limit 5
```

Licenses are preserved per file and vary (CC BY-NC-ND, all rights reserved, unknown). Availability here does not by itself grant commercial reuse, training or redistribution of derivatives; see [RIGHTS.md](RIGHTS.md). Originals may contain author names and signatures. Docs are in Spanish: [reuse guide](docs/REUTILIZAR.md), [full-text card](docs/FULLTEXT_DATASET_CARD.md), [packages](docs/PUBLICACION.md).

Read the [protocol](docs/PROTOCOLO.md), [source audit](docs/FUENTES.md), [dataset card](docs/DATASET_CARD.md), [public continuity](CONTEXTO_PUBLICO.md) and [10-record pilot report](reports/PILOTO.md). Run `make reproduce` with Python 3.11+ to **validate all 225 records** and separately rebuild the **10-record pilot analysis** offline. The complete-collection check produces [`research_225_validation.json`](reports/research_225_validation.json); analytical reports and figures remain limited to the pilot. See [publication scope](docs/PUBLICACION.md) and [rights by material](RIGHTS.md).
