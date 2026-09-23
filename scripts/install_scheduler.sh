#!/bin/bash
# Installs a per-user launchd agent that runs one cycle every 15 minutes while you are logged in,
# the Mac is awake, and (checked by the cycle itself) online. No admin rights, no system settings.
set -euo pipefail
PROJ="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="com.papertradingsim.cycle"
SUPPORT="$HOME/Library/Application Support/PaperTradingSim"
LOGDIR="$HOME/Library/Logs/PaperTradingSim"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
mkdir -p "$SUPPORT" "$LOGDIR" "$HOME/Library/LaunchAgents"
sed "s|__PROJECT__|$PROJ|" "$PROJ/scripts/run_cycle.sh" > "$SUPPORT/run_cycle.sh"
chmod 755 "$SUPPORT/run_cycle.sh"
cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array><string>/bin/bash</string><string>$SUPPORT/run_cycle.sh</string></array>
  <key>StartInterval</key><integer>900</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>$LOGDIR/launchd.out.log</string>
  <key>StandardErrorPath</key><string>$LOGDIR/launchd.err.log</string>
  <key>EnvironmentVariables</key>
  <dict><key>PATH</key><string>/usr/bin:/bin:/usr/sbin:/sbin</string><key>LANG</key><string>en_US.UTF-8</string></dict>
</dict>
</plist>
PL
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl enable "gui/$(id -u)/$LABEL"
echo "installed $LABEL (every 15 min; first run now). Logs: $LOGDIR"
