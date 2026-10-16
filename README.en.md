<p align="right"><a href="README.md">ES</a> · <strong>EN</strong></p>

![Synesis](assets/banner.png)

# Synesis

Reproducible research on university capstone and master's theses across the generative AI transition. Spanish is the primary language. Universidad Europea de Valencia is mandatory in the design.

This repository publishes **225 real metadata records from six sources**, following an audit of 13 institutions: Universidad Europea de Valencia (90), UPV (100), MIT (10), TU Berlin (10), HKUST (10) and USP (5). Download the complete collection from [`data/research_225/`](data/research_225/), with its [manifest](data/research_225/manifest.json).

The 225 metadata records are published with permission confirmed by the project owner, recorded in [`PERMISSIONS.json`](data/research_225/PERMISSIONS.json), while preserving source licenses.

A separate **10-record CC0 pilot from TU Berlin**, [`data/pilot/rights_cleared.jsonl`](data/pilot/rights_cleared.jsonl), drives the analytical pipeline, reports and figures. These 10 records are already included in the 225: there are **225 unique works, not 235**.

Both collections come from convenience sampling and do not estimate AI adoption or causal effects. Repository dates do not automatically mean defense dates. No PDFs, full text, abstracts, author/contact fields, completed human labels or trained model weights are distributed. No model has been trained on these works.

Read the [protocol](docs/PROTOCOLO.md), [source audit](docs/FUENTES.md), [dataset card](docs/DATASET_CARD.md), [public continuity](CONTEXTO_PUBLICO.md) and [10-record pilot report](reports/PILOTO.md). Run `make reproduce` with Python 3.11+ to **validate all 225 records** and separately rebuild the **10-record pilot analysis** offline. The complete-collection check produces [`research_225_validation.json`](reports/research_225_validation.json); analytical reports and figures remain limited to the pilot. See [publication scope](docs/PUBLICACION.md) and [rights by material](RIGHTS.md).
