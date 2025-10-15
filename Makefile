.PHONY: setup fmt lint mypy test cov docs demo demo-ui

setup:
	python -m pip install --upgrade pip
	pip install -e .[dev,docs]

fmt:
	ruff format .

lint:
	ruff check .

mypy:
	mypy sentrykit

test:
	pytest

cov:
	pytest --cov=sentrykit --cov-report=term-missing

docs:
	mkdocs build

demo:
	python examples/openai_agents_demo/demo.py

demo-ui:
	uvicorn demo_app.main:app --reload
