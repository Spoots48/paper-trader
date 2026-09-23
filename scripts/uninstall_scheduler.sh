#!/bin/bash
# Stops and removes the launchd agent. Ledgers, reports and data are left untouched.
LABEL="com.papertradingsim.cycle"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/$LABEL.plist"
echo "scheduler removed (data kept)"
