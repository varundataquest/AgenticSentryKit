# Installation

Most contributors create a fresh virtual environment and install the editable package with development extras:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,docs]"
```

Production deployments can install `sentrykit` from a published package and layer in only the extras they need:

- `openai_agents`
- `langchain`
- `autogen`
- `strands`
- `crewai`
- `docs`
- `dev`

Each extra is a small dependency group for the related adapter or tooling. Treat them as optional add-ons and pin versions according to your release process.
