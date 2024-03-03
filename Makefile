.PHONY: run format setup-db

run:
		python -m main

format:
		isort . ; ruff check --fix ; ruff format ; black .

setup-db:
		python scripts/setup_db.py
