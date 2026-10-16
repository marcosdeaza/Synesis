PYTHON ?= python3

.PHONY: reproduce check test figures
reproduce: check test

check:
	PYTHONPATH=src $(PYTHON) -m synesis.cli check

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

figures:
	$(PYTHON) scripts/render_figures.py
