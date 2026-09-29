#!/bin/bash
# Installs a per-user launchd agent that runs one cycle every 15 minutes while you are logged in,
# the Mac is awake, the external drive is mounted and (checked by the cycle itself) online.
# Everything project-related lives on the external drive; only the LaunchAgents plist (OS registration) is local.
# NOTE: on macOS a launchd-spawned /bin/bash is denied access to the external volume (job exits 126) unless the user grants
# /bin/bash "Removable Volumes" (or Full Disk Access) in System Settings > Privacy & Security. That is a security setting the
# user must grant; after that this installer works. Without it the cloud (GitHub Actions) still trades; the Paper Trader app syncs while open.
set -euo pipefail
HOME_DIR="/Volumes/X10 Pro/Paper Trading Sim"
[ -d "$HOME_DIR/installed/runtime" ] || { echo "external drive not mounted or runtime missing: $HOME_DIR/installed/runtime" >&2; exit 1; }
PROJ="$HOME_DIR/installed/runtime"
LABEL="com.papertradingsim.cycle"
LOGDIR="$HOME_DIR/installed/logs"
LAUNCHER="$HOME_DIR/installed/run_cycle.sh"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
mkdir -p "$LOGDIR" "$HOME/Library/LaunchAgents"
sed -e "s|__PROJECT__|$PROJ|" -e "s|__HOME_DIR__|$HOME_DIR|" "$(cd "$(dirname "$0")" && pwd)/run_cycle.sh" > "$LAUNCHER"
chmod 755 "$LAUNCHER"
cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array><string>/bin/bash</string><string>$LAUNCHER</string></array>
  <key>StartInterval</key><integer>900</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>/dev/null</string>
  <key>StandardErrorPath</key><string>/dev/null</string>
  <key>EnvironmentVariables</key>
  <dict><key>PATH</key><string>/usr/bin:/bin:/usr/sbin:/sbin</string><key>LANG</key><string>en_US.UTF-8</string></dict>
</dict>
</plist>
PL
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl enable "gui/$(id -u)/$LABEL"
echo "installed $LABEL (every 15 min; first run now). Launcher: $LAUNCHER. Logs: $LOGDIR"
