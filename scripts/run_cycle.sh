#!/bin/bash
# Launched by launchd every 15 minutes (installed copy lives in ~/Library/Application Support/PaperTradingSim/).
# Runs one idempotent cycle. Exits quietly when the project drive is missing; the Python side
# also exits quietly when offline or paused.
PROJ="__PROJECT__"
LOGDIR="$HOME/Library/Logs/PaperTradingSim"
mkdir -p "$LOGDIR"
ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
if [ ! -d "$PROJ" ] || [ ! -x "$PROJ/.venv/bin/python" ]; then
  echo "$(ts) project not reachable at $PROJ (drive unplugged?); skipping" >> "$LOGDIR/launcher.log"
  exit 0
fi
cd "$PROJ" || { echo "$(ts) cannot cd into $PROJ (permission?)" >> "$LOGDIR/launcher.log"; exit 0; }
"$PROJ/.venv/bin/python" "$PROJ/run.py" cycle --trigger launchd >> "$LOGDIR/launcher.log" 2>&1
code=$?
echo "$(ts) cycle exit $code" >> "$LOGDIR/launcher.log"
exit 0
