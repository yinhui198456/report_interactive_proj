#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

echo "=== Publish Dry-Run Check ==="
echo "Project directory: $PROJECT_DIR"
echo ""

echo "[1/5] Cleaning caches..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -name '*.pyc' -delete 2>/dev/null || true
rm -rf .pytest_cache tests/__pycache__ 2>/dev/null || true
echo "done"
echo ""

echo "[2/5] Checking sensitive/cache files before tests..."
if [ -f "data/config.local.json" ]; then
  echo "WARNING: data/config.local.json exists - should not be committed"
else
  echo "data/config.local.json: not present (good)"
fi
if [ -d ".pytest_cache" ] || [ -d "__pycache__" ] || find . -name '*.pyc' | grep -q .; then
  echo "WARNING: cache files still present"
else
  echo "cache files: not present (good)"
fi
echo ""

echo "[3/5] Running pytest..."
pytest -q
echo ""

echo "[3.5/5] Re-cleaning caches after pytest..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -name '*.pyc' -delete 2>/dev/null || true
rm -rf .pytest_cache tests/__pycache__ 2>/dev/null || true
echo "done"
echo ""

echo "[4/5] Checking workspace-root import..."
cd /opt/personal-agent-workspace
python3 -c "import report_interactive_proj.main; print('ok')"
cd "$PROJECT_DIR"
echo ""

echo "[5/5] Git status for project directory..."
git -c safe.directory=/opt/personal-agent-workspace status --short .
echo ""

echo "=== Summary ==="
echo "No push, commit, remote modification, or repo creation was performed."
echo "Review the output above before proceeding to user-confirmed commands."
