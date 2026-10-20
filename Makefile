PYTHON ?= python3

.PHONY: reproduce check test figures corpus parquet download acquire validate-pdfs
reproduce: check test

check:
	PYTHONPATH=src $(PYTHON) -m synesis.cli check
	$(PYTHON) scripts/check_research_snapshot.py
	$(PYTHON) scripts/prepare_research.py
	$(PYTHON) scripts/check_fulltext.py

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

figures:
	$(PYTHON) scripts/render_figures.py
	$(PYTHON) scripts/render_collection.py

corpus:
	$(PYTHON) scripts/build_corpus.py

parquet:
	$(PYTHON) scripts/export_parquet.py

download:
	$(PYTHON) scripts/download_release.py --tag v0.2.0

acquire:
	$(PYTHON) scripts/acquire_spain.py
	$(PYTHON) scripts/acquire_global.py

validate-pdfs:
	$(PYTHON) scripts/check_fulltext.py --require-files
