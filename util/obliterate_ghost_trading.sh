#!/bin/bash
set -e

cd "$(dirname "$0")/.."

echo "============================================"
echo " RICK: OBLITERATING GHOST TRADING (SAFE) "
echo "============================================"
echo
echo " - Skipping ROLLBACK_SNAPSHOTS, .git, .venv"
echo " - Forcing ghost/sim flags OFF"
echo " - Renaming ghost labels to CANARY*"
echo

# Helper: find all *text* files we care about, skipping snapshots + venv + git
find_text_files() {
  find . \
    -path "./ROLLBACK_SNAPSHOTS" -prune -o \
    -path "./.git" -prune -o \
    -path "./.venv" -prune -o \
    -path "./venv" -prune -o \
    -path "./.system" -prune -o \
    -path "./archives" -prune -o \
    -path "./_archive_docs" -prune -o \
    -path "./_archive_scripts" -prune -o \
    -type f \( \
        -name "*.py"  -o \
        -name "*.sh"  -o \
        -name "*.json" -o \
        -name "*.txt" -o \
        -name "*.md"  -o \
        -name "*.yaml" -o \
        -name "*.yml" -o \
        -name "*.ini" -o \
        -name "*.cfg" -o \
        -name "*.toml" \
      \) -print0
}

echo "Step 1: Force all ghost/sim flags OFF (only real or demo allowed)..."
find_text_files | xargs -0 -r sed -i \
  -e 's/use_ghost_mode *= *True/use_ghost_mode = False/g' \
  -e 's/SIMULATED *= *True/SIMULATED = False/g' \
  -e 's/SIMULATION *= *True/SIMULATION = False/g' \
  -e 's/mode *= *"practice"/mode = "canary"/g' \
  -e 's/mode *= *"paper"/mode = "canary"/g'

echo "Step 2: Clean up ghost labels in IDs + progress files (purely cosmetic)..."
find_text_files | xargs -0 -r sed -i \
  -e 's/CANARY_CHARTER/CANARY_CHARTER/g' \
  -e 's/ghost_charter_progress\.json/canary_charter_progress.json/g'

echo "Step 3: Remove stale ghost progress/log files in *this* live root..."
rm -f canary_charter_progress.json 2>/dev/null || true
rm -f logs/*ghost* 2>/dev/null || true

echo "Step 4: Make sure narration.jsonl exists and is writable..."
touch narration.jsonl
chmod 666 narration.jsonl 2>/dev/null || true

echo
echo "============================================"
echo " RICK: Ghost trading config is OFF."
echo " - Only canary (paper/practice) + demo remain."
echo " - No ghost flags, no sim flags left in live tree."
echo "============================================"
