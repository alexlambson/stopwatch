
test:
	@echo "Running tests without coverage"
	python -m pytest

test-coverage:
	@echo "Running tests and generating coverage report......."
	python -m pytest -v --cov --cov-report html

build-docs:
	@echo "Building docs to 'docs/_build'"
	pip install -r ./docs/requirements.txt
	sphinx-build -b html docs/ docs/_build

build:
	rm -rf dist/*
	pip install -r requirements-dev.txt
	python -m build

publish:
	make build
	python -m twine upload dist/*
