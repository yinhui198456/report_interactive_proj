#!/bin/bash
set -euo pipefail

# Switch to script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8010}"

exec python3 -m uvicorn main:app --host "$HOST" --port "$PORT"
