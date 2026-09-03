.PHONY: install test lint typecheck clean

install:
	pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check msand_sdl tests scripts

typecheck:
	mypy msand_sdl

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache build dist *.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
