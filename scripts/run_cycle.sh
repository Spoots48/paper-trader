#!/bin/bash
# Launched by launchd every 15 minutes. The installed copy lives on the external drive
# (/Volumes/X10 Pro/Paper Trading Sim/installed/run_cycle.sh); the plist in ~/Library/LaunchAgents is OS registration only.
# Runs one idempotent cycle. If the drive is missing nothing is created anywhere and the run is skipped.
# The Python exit code is preserved so failures are visible to launchd.
PROJ="__PROJECT__"
HOME_DIR="__HOME_DIR__"
LOGDIR="$HOME_DIR/installed/logs"
ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
if [ ! -d "$HOME_DIR" ] || [ ! -d "$LOGDIR" ] || [ ! -x "$PROJ/.venv/bin/python" ]; then
  echo "$(ts) external drive/project not reachable at $HOME_DIR; skipping" >&2
  exit 0
fi
export TMPDIR="$HOME_DIR/.cache/tmp"
export UV_CACHE_DIR="$HOME_DIR/.cache/uv" HF_HOME="$HOME_DIR/.cache/huggingface" TORCH_HOME="$HOME_DIR/.cache/torch"
export PYTHONPYCACHEPREFIX="$HOME_DIR/.cache/pycache" PYTHONDONTWRITEBYTECODE=1
mkdir -p "$TMPDIR" || exit 0
cd "$PROJ" || { echo "$(ts) cannot cd into $PROJ" >> "$LOGDIR/launcher.log"; exit 1; }
"$PROJ/.venv/bin/python" "$PROJ/run.py" cycle --trigger launchd >> "$LOGDIR/launcher.log" 2>&1
code=$?
echo "$(ts) cycle exit $code" >> "$LOGDIR/launcher.log"
exit $code
