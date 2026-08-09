#!/usr/bin/env bash
# Run the same checks CI runs, locally, before pushing.
# Usage: bash scripts/local_check.sh

set -e
cd "$(dirname "$0")/.."

if command -v python3 &> /dev/null; then
  PYTHON_CMD=python3
elif command -v python &> /dev/null; then
  PYTHON_CMD=python
else
  echo "No Python interpreter found (tried python3 and python). Install Python 3 to run this check."
  exit 1
fi

echo "== 1. Checking required folders =="
for dir in chapters docs assets assessments quality-audits templates; do
  if [ ! -d "$dir" ]; then
    echo "MISSING: $dir"
    exit 1
  fi
done
echo "OK"

echo ""
echo "== 2. Scanning for placeholder text =="
if grep -rniE "lorem ipsum|\[insert[^]]*\]|\bTODO\(fill\)|\bFIXME\b|xxx{2,}" \
    --include="*.html" --include="*.md" chapters/ docs/ assessments/ 2>/dev/null; then
  echo "Found placeholder text above -- fix before pushing."
  exit 1
fi
echo "OK"

echo ""
echo "== 3. Python syntax check =="
shopt -s globstar nullglob
FILES=(chapters/**/*.py)
if [ ${#FILES[@]} -eq 0 ]; then
  echo "No Python files yet -- skipping."
else
  $PYTHON_CMD -m py_compile "${FILES[@]}"
  echo "OK"
fi

echo ""
echo "== 4. Running every exercises/solution.py, project/solution.py, and practice/solution.py =="
echo "(this requires the course's SDK installed in your active environment)"
FAIL=0
# See ci.yml for the full explanation of the CI: LONG_RUNNING_SERVER and
# CI: NEEDS_LIVE_SERVER=<path> marker-comment convention.
for f in chapters/*/exercises/solution.py chapters/*/project/solution.py chapters/*/practice/solution.py; do
  [ -f "$f" ] || continue
  dir=$(dirname "$f")

  if grep -q "# CI: LONG_RUNNING_SERVER" "$f"; then
    OUT=$(cd "$dir" && timeout 5 $PYTHON_CMD solution.py 2>&1 || true)
    if echo "$OUT" | grep -q "Traceback"; then
      echo "$OUT"
      echo "FAIL: $f raised an unhandled exception"
      FAIL=1
    fi
  elif grep -q "# CI: NEEDS_LIVE_SERVER=" "$f"; then
    SERVER_REL=$(grep -oP '# CI: NEEDS_LIVE_SERVER=\K\S+' "$f")
    (cd "$(dirname "$SERVER_REL")" && nohup $PYTHON_CMD "$(basename "$SERVER_REL")" > /tmp/ci-server.log 2>&1 &
     echo $! > /tmp/ci-server.pid)
    sleep 2
    OUT=$(cd "$dir" && timeout 10 $PYTHON_CMD solution.py 2>&1)
    if echo "$OUT" | grep -q "Traceback"; then
      echo "$OUT"
      echo "FAIL: $f raised an unhandled exception"
      FAIL=1
    fi
    kill "$(cat /tmp/ci-server.pid)" 2>/dev/null || true
    rm -f /tmp/ci-server.pid /tmp/ci-server.log
  elif grep -q "sys.stdin" "$f"; then
    if ! (cd "$dir" && printf 'quit\n' | timeout 20 $PYTHON_CMD solution.py > /tmp/local_check_out.log 2>&1); then
      cat /tmp/local_check_out.log
      echo "FAIL: $f"
      FAIL=1
    fi
  else
    if ! (cd "$dir" && timeout 20 $PYTHON_CMD solution.py > /tmp/local_check_out.log 2>&1); then
      cat /tmp/local_check_out.log
      echo "FAIL: $f"
      FAIL=1
    fi
  fi
done
find chapters -name "bookmarks.json" -delete
rm -f /tmp/local_check_out.log
if [ "$FAIL" -ne 0 ]; then
  echo "One or more solution.py files failed -- see above."
  exit 1
fi
echo "OK"

echo ""
echo "== 5. JS syntax + chapter-path validation =="
if command -v node &> /dev/null; then
  for f in assets/*.js; do
    node --check "$f"
  done
  node -e '
    global.window = {};
    require("./assets/chapters-data.js");
    const fs = require("fs");
    let missing = 0;
    for (const mod of window.ACAFE_MODULES) {
      for (const ch of mod.chapters) {
        if (ch.path && !fs.existsSync(ch.path)) {
          console.error("Broken chapter path:", ch.path);
          missing++;
        }
      }
      if (mod.examPath && !fs.existsSync(mod.examPath)) {
        console.error("Broken examPath:", mod.examPath);
        missing++;
      }
    }
    if (missing > 0) { process.exit(1); }
  '
  echo "OK"
else
  echo "node not found -- skipping JS checks (CI will still run them)"
fi

echo ""
echo "== 6. Scanning for likely secrets =="
PATTERN='sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|api[_-]?key\s*=\s*["\047][A-Za-z0-9]{16,}'
if grep -rniE "$PATTERN" \
    --include="*.py" --include="*.md" --include="*.json" --include="*.yml" --include="*.yaml" --include="*.html" \
    --exclude-dir=".git" . 2>/dev/null; then
  echo "Possible secret detected above -- remove before pushing."
  exit 1
fi
echo "OK"

echo ""
echo "All local checks passed. Safe to push."
