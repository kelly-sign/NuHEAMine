#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$ROOT"

if [ ! -f .env ]; then
  echo "Missing .env. Copy .env.example to .env and configure it first." >&2
  exit 1
fi

if [ ! -x .venv/bin/python ]; then
  echo "Missing .venv. Create the Python 3.8 environment and install requirements.txt first." >&2
  exit 1
fi

if [ ! -x node_modules/.bin/vue-cli-service ]; then
  echo "Missing node_modules. Run npm ci first." >&2
  exit 1
fi

.venv/bin/python manage.py runserver 127.0.0.1:8000 &
BACKEND_PID=$!
npm run serve &
FRONTEND_PID=$!

cleanup() {
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup INT TERM EXIT
wait

