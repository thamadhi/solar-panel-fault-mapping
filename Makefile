.PHONY: run api app test lint format install clean

# Default target
run: api

# Run Flask API (backend)
api:
	python -m src.api

# Run Streamlit dashboard (frontend)
app:
	python -m streamlit run app.py

# Run unit tests
test:
	pytest tests/

# Lint
lint:
	flake8 src tests

# Format
format:
	black src tests

# Install dependencies
install:
	pip install -r requirements.txt

# Clean cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
