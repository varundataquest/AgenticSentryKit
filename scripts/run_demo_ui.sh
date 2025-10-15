#!/usr/bin/env bash
set -euo pipefail

# Launch the SentryKit demo UI with sensible defaults.
# Usage: PORT=8765 ./scripts/run_demo_ui.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PORT="${PORT:-8765}"

if [[ ! -x ./.venv/bin/python ]]; then
  echo "[setup] Creating virtualenv at .venv (python3.11 if available)..."
  if command -v python3.11 >/dev/null 2>&1; then
    python3.11 -m venv .venv
  else
    python3 -m venv .venv
  fi
fi

echo "[setup] Activating virtualenv..."
source .venv/bin/activate

# Check required packages without attempting network installs in constrained environments.
if ! python - <<'PY'
import sys
try:
    import fastapi  # noqa: F401
    import uvicorn  # noqa: F401
except Exception as exc:
    sys.exit(1)
PY
then
  echo "[error] Missing demo dependencies (fastapi/uvicorn)." >&2
  echo "        Please run: pip install -e '.[demo]'" >&2
  exit 2
fi

echo "[run] Starting demo UI on http://127.0.0.1:${PORT}"
echo "      Reports dir: ${SENTRYKIT_DEMO_REPORTS_DIR:-demo_app/generated_reports}"
exec uvicorn demo_app.main:app --port "${PORT}"
