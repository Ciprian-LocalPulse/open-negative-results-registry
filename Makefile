# Makefile for open-negative-results-registry
#
# Every target here wraps a command already documented in README.md,
# with correct argument names verified against the actual scripts in
# scripts/ at the time this file was written. Run `make help` for a
# summary.

.PHONY: help install install-dev test validate analyze export search-index \
        docker-build docker-run clean

PYTHON ?= python3
PIP ?= pip
DATA_DIR ?= data/
EXPORT_FILE ?= DarkData_Export.xlsx

help:
	@echo "open-negative-results-registry -- available targets:"
	@echo "  make install       Install runtime dependencies"
	@echo "  make install-dev   Install runtime + dev/test dependencies"
	@echo "  make test          Run the pytest suite"
	@echo "  make validate      Validate every entry under $(DATA_DIR)"
	@echo "  make analyze       Print top trends across the dataset (--top 20)"
	@echo "  make export        Export the dataset to $(EXPORT_FILE)"
	@echo "  make search-index  Regenerate site/data_index.json"
	@echo "  make docker-build  Build the CLI toolkit container locally"
	@echo "  make docker-run    Run 'validate' inside the built container"
	@echo "  make clean         Remove generated artifacts (__pycache__, exports)"

install:
	$(PIP) install -r requirements.txt --break-system-packages

install-dev:
	$(PIP) install -r requirements.txt -r requirements-dev.txt --break-system-packages

test:
	pytest tests/ -v

validate:
	$(PYTHON) scripts/validate_submission.py $(DATA_DIR)

analyze:
	$(PYTHON) scripts/analyze_trends.py --top 20

export:
	$(PYTHON) scripts/export_to_excel.py --output $(EXPORT_FILE)

search-index:
	$(PYTHON) scripts/generate_search_index.py

docker-build:
	docker build -t darkdata-medicine .

docker-run: docker-build
	docker run --rm darkdata-medicine validate data/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -f $(EXPORT_FILE)
