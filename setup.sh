#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

log() {
  printf '[setup] %s\n' "$1"
}

require_cmd() {
  local cmd="$1"
  local hint="$2"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    printf '[setup] Missing required command: %s\n' "$cmd" >&2
    printf '[setup] %s\n' "$hint" >&2
    exit 1
  fi
}

copy_if_missing() {
  local source_file="$1"
  local target_file="$2"
  if [[ -f "$target_file" ]]; then
    log "Keeping existing $(basename "$target_file")"
    return
  fi
  cp "$source_file" "$target_file"
  log "Created $(basename "$target_file") from $(basename "$source_file")"
}

require_cmd "python3" "Install Python 3.10+ and re-run this script."
require_cmd "npm" "Install Node.js (includes npm) and re-run this script."

if [[ ! -f "$BACKEND_DIR/requirements.txt" || ! -f "$FRONTEND_DIR/package.json" ]]; then
  printf '[setup] Run this script from the project root.\n' >&2
  exit 1
fi

copy_if_missing "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
copy_if_missing "$FRONTEND_DIR/.env.local.example" "$FRONTEND_DIR/.env.local"

if [[ ! -d "$BACKEND_DIR/.venv" ]]; then
  log "Creating backend virtual environment (.venv)"
  python3 -m venv "$BACKEND_DIR/.venv"
else
  log "Using existing backend virtual environment (.venv)"
fi

log "Installing backend dependencies"
PIP_DISABLE_PIP_VERSION_CHECK=1 "$BACKEND_DIR/.venv/bin/pip" install -r "$BACKEND_DIR/requirements.txt"

log "Installing frontend dependencies"
(cd "$FRONTEND_DIR" && npm install)

cat <<'EOF'

[setup] Setup complete.

Run backend:
  cd backend
  source .venv/bin/activate
  uvicorn app.main:app --reload --port 8000

Run frontend (new terminal):
  cd frontend
  npm run dev

Use:
  Frontend: http://localhost:3000
  Backend:  http://localhost:8000
EOF
