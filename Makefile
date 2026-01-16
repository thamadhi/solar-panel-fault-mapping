run:
	python main.py

test:
	pytest tests/

lint:
	flake8 core handlers tests

format:
	black core handlers tests

install:
	pip install -r requirements.txt

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete