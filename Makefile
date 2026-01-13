.PHONY: setup run test clean lint format help venv

VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
BLACK := $(VENV)/bin/black
RUFF := $(VENV)/bin/ruff
UVICORN := $(VENV)/bin/uvicorn

help:
	@echo "AegisX - Available targets:"
	@echo "  make setup   - Create virtual environment and install dependencies"
	@echo "  make run     - Run the FastAPI server"
	@echo "  make test    - Run tests with pytest"
	@echo "  make lint    - Run linting checks"
	@echo "  make format  - Format code with black"
	@echo "  make clean   - Remove cache and temporary files"
	@echo "  make venv    - Create virtual environment only"

venv:
	@if [ ! -d "$(VENV)" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv $(VENV); \
		echo "Virtual environment created at ./$(VENV)"; \
	else \
		echo "Virtual environment already exists at ./$(VENV)"; \
	fi

setup: venv
	@echo "Setting up AegisX..."
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	@mkdir -p data
	@mkdir -p logs
	@echo ""
	@echo "Setup complete!"
	@echo "Virtual environment is at: ./$(VENV)"
	@echo "To activate manually: source $(VENV)/bin/activate"

run: venv
	@if [ ! -f "$(PYTHON)" ]; then \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "Starting AegisX AI Engine..."
	$(UVICORN) ai_engine.main:app --reload --host 0.0.0.0 --port 8000

test: venv
	@if [ ! -f "$(PYTEST)" ]; then \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "Running tests..."
	$(PYTEST) tests/ -v --cov=ai_engine --cov-report=term-missing

lint: venv
	@if [ ! -f "$(RUFF)" ]; then \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "Running linting checks..."
	$(RUFF) check ai_engine/
	$(BLACK) --check ai_engine/

format: venv
	@if [ ! -f "$(BLACK)" ]; then \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "Formatting code..."
	$(BLACK) ai_engine/
	$(RUFF) check --fix ai_engine/

clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/
	@echo "Clean complete!"

clean-all: clean
	@echo "Removing virtual environment..."
	rm -rf $(VENV)
	@echo "All clean!"
