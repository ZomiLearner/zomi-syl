# ----------------------------------------
# Variables (can be overridden on CLI)
# ----------------------------------------
PYTHON ?= python3
URL ?=
SHEET ?=
TRAINING ?= data/zomi_only.tsv
VERSION ?=

MODEL ?=
HF_REPO ?=
VERSION ?=

BUNDLED_DIR = src/zomi_syl/models/bundled/$(MODEL)
MODELS_DIR = src/zomi_syl/models/$(MODEL)

# ----------------------------------------
# Default target
# ----------------------------------------
.DEFAULT_GOAL := help


.PHONY: get_golden_crf_frozen_data
get_golden_crf_frozen_data:
	@if [ -z "$(URL)" ]; then \
		echo "Error: URL is required. Usage:"; \
		echo "  make get_golden_crf_frozen_data URL=<google-sheet-url>"; \
		echo "Examples:"; \
		echo "  make get_golden_crf_frozen_data URL='https://docs.google.com/spreadsheets/d/XXXX/edit#gid=0'"; \
		echo "  make get_golden_crf_frozen_data URL='https://docs.google.com/spreadsheets/d/XXXX/edit#gid=0' SHEET='Sheet1'"; \
		exit 1; \
	fi
	$(PYTHON) scripts/get_golden_crf_frozen_data.py --url "$(URL)" --sheet "$(SHEET)"

# ----------------------------------------
# Get zomi_syllabified_human from Google Sheet
# ----------------------------------------
.PHONY: get-zomi-syllabified-human
get-zomi-syllabified-human:
	@echo "🧹 Generating data/get_zomi_syllabified_human.tsv ..."
		@if [ -z "$(URL)" ]; then \
		echo "Error: URL is required. Usage:"; \
		echo "  make get_zomi_syllabified_human URL=<google-sheet-url>"; \
		echo "Examples:"; \
		echo "  make get_zomi_syllabified_human URL='https://docs.google.com/spreadsheets/d/XXXX/edit#gid=0'"; \
		echo "  make get_zomi_syllabified_human URL='https://docs.google.com/spreadsheets/d/XXXX/edit#gid=0' SHEET='Sheet1'"; \
		exit 1; \
	fi
	$(PYTHON) scripts/get_zomi_syllabified_human.py --url "$(URL)" --sheet "$(SHEET)"
	@echo "✓ data/get_zomi_syllabified_human.tsv generated."

# ----------------------------------------
# Clean dataset
# ----------------------------------------
.PHONY: clean-dataset
clean-dataset:
	@echo "🧹 Cleaning get_zomi_syllabified_human.tsv... to generate zomi_only.tsv, non_zomi.tsv, and mixed_unsure.tsv"
	$(PYTHON) scripts/clean_dataset.py
	@echo "✓ Dataset cleaned."

# ----------------------------------------
# Train CRF model
# ----------------------------------------
.PHONY: train-crf
train-crf: # get-zomi-syllabified-human clean-dataset
	@echo "🔄 Training CRF model..."
	$(PYTHON) -m scripts.train_crf \
        --input training/data/zomi_only.tsv \
        --output training/model/crf/
	@echo "✓ Training complete. Model saved in ./model/"

# ----------------------------------------
# Freeze CRF model
# Usage:
#   make freeze-crf VERSION=v3
#   make freeze-crf        # auto-increment
# ----------------------------------------
.PHONY: freeze-crf
freeze-crf: train-crf get_golden_crf_frozen_data
	@if [ -z "$(VERSION)" ]; then \
		echo "ℹ️  VERSION not provided. Detecting latest version..."; \
		LATEST=$$(ls -1 model/freeze 2>/dev/null | sort -V | tail -n 1); \
		if [ -z "$$LATEST" ]; then \
			echo "ℹ️  No previous versions found. Using VERSION=v1"; \
			VERSION=v1; \
		else \
			echo "ℹ️  Latest version: $$LATEST"; \
			NUM=$${LATEST#v}; \
			NEXT_NUM=$$((NUM + 1)); \
			VERSION=v$$NEXT_NUM; \
			echo "ℹ️  Auto-incremented VERSION=$$VERSION"; \
		fi; \
	else \
		echo "ℹ️  Using provided VERSION=$(VERSION)"; \
	fi; \
	\
	echo "📦 Freezing CRF model as $$VERSION..."; \
	mkdir -p model/freeze/$$VERSION; \
	cp data/crf_golden.tsv model/; \
	rsync -av --exclude "freeze" model/ model/freeze/$$VERSION/; \
	echo "✓ Freeze complete: model/freeze/$$VERSION"


# ----------------------------------------
# Push frozen CRF model to HuggingFace (new HF CLI)
# Usage:
#   make push-hf-crf VERSION=v3
#   make push-hf-crf        # auto-detect latest
# ----------------------------------------
.PHONY: push-hf-crf
push-hf-crf: freeze-crf
	@if [ -z "$(VERSION)" ]; then \
		echo "ℹ️  VERSION not provided. Detecting latest version..."; \
		LATEST=$$(ls -1 model/freeze 2>/dev/null | sort -V | tail -n 1); \
		if [ -z "$$LATEST" ]; then \
			echo "❌ No frozen versions found. Run 'make freeze-crf' first."; \
			exit 1; \
		fi; \
		echo "ℹ️  Latest version: $$LATEST"; \
		VERSION=$$LATEST; \
	else \
		echo "ℹ️  Using provided VERSION=$(VERSION)"; \
		VERSION=$(VERSION); \
	fi; \
	\
	echo "🚀 Pushing model version $$VERSION to HuggingFace..."; \
	hf upload zomi-language-corpora/zomi-crf-syllabifier model/freeze/$$VERSION . --revision $$VERSION; \
	echo "✓ HuggingFace upload complete (revision=$$VERSION)"


# ----------------------------------------
# Update HF main branch with a specific version
# If VERSION is provided → use it
# If VERSION is missing → use the latest version in model/freeze/
# ----------------------------------------
.PHONY: update-hf-main-crf
update-hf-main-crf: push-hf-crf
	@if [ -z "$(VERSION)" ]; then \
		echo "ℹ️ VERSION not provided. Using latest version in model/freeze/"; \
		VERSION=$$(ls -1 model/freeze | sort -V | tail -n 1); \
		echo "➡️ Using VERSION=$$VERSION"; \
		hf upload zomi-language-corpora/zomi-crf-syllabifier model/freeze/$$VERSION . --revision main; \
	else \
		echo "➡️ Updating main with VERSION=$(VERSION)"; \
		hf upload zomi-language-corpora/zomi-crf-syllabifier model/freeze/$(VERSION) . --revision main; \
	fi
	@echo "✓ main branch updated"

.PHONY: list-backends
list-backends:
	@echo ""
	@echo "⚙️  Available Backends"
	@echo "----------------------------------"
	@printf "%s\n" \
	"from zomi_syl.registry.models import list_models" \
	"for m in list_models():" \
	"    print(f'• {m}')" \
	| python3
	@echo ""


.PHONY: list-models
list-models:
	@echo ""
	@echo "📦 Installed Models"
	@echo "----------------------------------"
	@ls -1 src/zomi_syl/models | grep -v "__" | sed 's/^/• /'
	@echo ""

# ----------------------------------------
# Pull a model from its own HF model repo to src/zomi_syl/models/<model>/
# MODEL=crf / syllabifier / transformer / etc.
# HF_REPO=zomi-language-corpora/<repo>
# VERSION optional → defaults to main
# ----------------------------------------
.PHONY: pull-hf
pull-hf:
	@if [ -z "$(MODEL)" ]; then \
		echo "❌ MODEL is required (e.g., MODEL=crf)"; \
		exit 1; \
	fi

	@if [ -z "$(HF_REPO)" ]; then \
		echo "❌ HF_REPO is required (e.g., HF_REPO=zomi-language-corpora/zomi-crf-syllabifier)"; \
		exit 1; \
	fi

	@echo "📥 Pulling model '$(MODEL)' from HuggingFace repo '$(HF_REPO)'..."
	rm -rf $(MODELS_DIR)
	mkdir -p $(MODELS_DIR)

	@if [ -z "$(VERSION)" ]; then \
		echo "ℹ️ VERSION not provided → using revision=main"; \
		hf download $(HF_REPO) --revision main --local-dir $(MODELS_DIR); \
	else \
		echo "➡️ Using revision=$(VERSION)"; \
		hf download $(HF_REPO) --revision $(VERSION) --local-dir $(MODELS_DIR); \
	fi

	@echo "✓ Model downloaded into $(MODELS_DIR)"


# ----------------------------------------
# Build package
# ----------------------------------------
.PHONY: build
build:
	$(PYTHON) -m build

# ----------------------------------------
# Install
# ----------------------------------------
.PHONY: install
install:
	$(PYTHON) -m pip install .

.PHONY: dev-install
dev-install:
	$(PYTHON) -m pip install -e .[dev]

.PHONY: clean-pyc
clean-pyc:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# ----------------------------------------
# Generate changelog
# ----------------------------------------
.PHONY: changelog
changelog:
	@echo "Generating CHANGELOG.md..."
	@python3 scripts/generate_changelog.py
	@echo "Done."

# ----------------------------------------
# Lint & Format
# ----------------------------------------
.PHONY: lint
lint:
	ruff check src tests

.PHONY: format
format:
	ruff check --fix src tests
	black src tests

# ----------------------------------------
# Tests
# ----------------------------------------
.PHONY: test
test:
	pytest -q

.PHONY: test-verbose
test-verbose:
	pytest -vv

# ----------------------------------------
# Clean
# ----------------------------------------
.PHONY: clean
clean:
	rm -rf build dist *.egg-info
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete

tree:
	@echo "📁 $(notdir $(CURDIR))"
	@tree -C -I ".git|node_modules|__pycache__" .




# Auto-discover help scripts
HELP_SCRIPTS := $(wildcard scripts/help-*.sh)
HELP_TARGETS := $(patsubst scripts/help-%.sh,help-%,$(HELP_SCRIPTS))

.PHONY: $(HELP_TARGETS)
$(HELP_TARGETS):
	@bash scripts/$(@).sh


# ----------------------------------------
# Help
# ----------------------------------------
.PHONY: help
help:
	@echo ""
	@echo "Available make commands:"
	@echo ""
	@echo "  make sheet URL=<url> [SHEET=<sheet-name>]   - Load Google Sheet"
	@echo "  make golden TRAINING=<file>                 - Extract CRF golden set"
	@echo "  make build                                  - Build wheel + sdist"
	@echo "  make install                                - Install package"
	@echo "  make dev-install                            - Install in editable mode"
	@echo "  make lint                                   - Run ruff"
	@echo "  make format                                 - Auto-format"
	@echo "  make test                                   - Run pytest"
	@echo "  make test-verbose                           - Run pytest with verbose output"
	@echo "  make clean                                  - Remove build artifacts"
	@echo ""


allhelp: help help-cli list-backends list-models help-devs


# Change the version number in toml file and run this
# git add . && git commit -m "Bump version from v0.1.907 to v0.1.908" && git push && git tag v0.1.908 && git push origin v0.1.908

# Delete/Remove a tag and re-tag
# git tag -d v0.1.905
# git push origin --delete v0.1.905
# git tag v0.1.906
# git push -f origin v0.1.906