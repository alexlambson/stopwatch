
test:
	@echo "Running tests without coverage"
	python -m pytest

test-coverage:
	@echo "Running tests and generating coverage report......."
	python -m pytest -v --cov --cov-report html
