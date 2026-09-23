#!/bin/bash
# Builds "Paper Trader.app" with the Xcode Command Line Tools (no Xcode, no Apple ID, free)
# and installs it to ~/Applications. Usage: bash app/build_app.sh
set -euo pipefail
PROJ="$(cd "$(dirname "$0")/.." && pwd)"
BUILD="$PROJ/app/build"
APP="$BUILD/Paper Trader.app"
DEST="$HOME/Applications/Paper Trader.app"
rm -rf "$BUILD"; mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources" "$BUILD/icon.iconset"

swiftc -O -o "$APP/Contents/MacOS/PaperTrader" "$PROJ/app/PaperTrader.swift" -framework Cocoa -framework WebKit

# icon
swiftc -O -o "$BUILD/make_icon" "$PROJ/app/make_icon.swift" -framework Cocoa
"$BUILD/make_icon" "$BUILD/icon_1024.png"
for s in 16 32 128 256 512; do
  sips -z $s $s "$BUILD/icon_1024.png" --out "$BUILD/icon.iconset/icon_${s}x${s}.png" >/dev/null
  d=$((s * 2)); sips -z $d $d "$BUILD/icon_1024.png" --out "$BUILD/icon.iconset/icon_${s}x${s}@2x.png" >/dev/null
done
iconutil -c icns "$BUILD/icon.iconset" -o "$APP/Contents/Resources/AppIcon.icns"

cat > "$APP/Contents/Info.plist" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key><string>Paper Trader</string>
  <key>CFBundleDisplayName</key><string>Paper Trader</string>
  <key>CFBundleIdentifier</key><string>local.papertradingsim.app</string>
  <key>CFBundleExecutable</key><string>PaperTrader</string>
  <key>CFBundleIconFile</key><string>AppIcon</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>1.0</string>
  <key>CFBundleVersion</key><string>1</string>
  <key>LSMinimumSystemVersion</key><string>13.0</string>
  <key>NSHighResolutionCapable</key><true/>
  <key>PTProjectPath</key><string>$PROJ</string>
  <key>NSAppTransportSecurity</key><dict><key>NSAllowsLocalNetworking</key><true/></dict>
  <key>NSHumanReadableCopyright</key><string>Paper trading research tool. No real money.</string>
</dict>
</plist>
PL
codesign --force --deep -s - "$APP" >/dev/null
mkdir -p "$HOME/Applications"
rm -rf "$DEST"
cp -R "$APP" "$DEST"
echo "installed: $DEST"
