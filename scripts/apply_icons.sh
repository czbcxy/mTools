#!/bin/bash
# Build icns from PNG masters, inject into the three toolbar apps, re-sign.
set -e
APPS="/Users/chengzhengbo/WorkBuddy/super-addr/apps"
SRC="/tmp/icicons2"

make_icns() {
  local png="$1" local icns="$2"
  local d
  d=$(mktemp -d)
  mkdir -p "$d/icon.iconset"
  sips -z 1024 1024 "$png" --out "$d/icon.iconset/icon_512x512@2x.png" >/dev/null 2>&1
  sips -z 512 512   "$png" --out "$d/icon.iconset/icon_512x512.png"    >/dev/null 2>&1
  sips -z 512 512   "$png" --out "$d/icon.iconset/icon_256x256@2x.png" >/dev/null 2>&1
  sips -z 256 256   "$png" --out "$d/icon.iconset/icon_256x256.png"    >/dev/null 2>&1
  sips -z 256 256   "$png" --out "$d/icon.iconset/icon_128x128@2x.png" >/dev/null 2>&1
  sips -z 128 128   "$png" --out "$d/icon.iconset/icon_128x128.png"    >/dev/null 2>&1
  sips -z 64 64     "$png" --out "$d/icon.iconset/icon_32x32@2x.png"   >/dev/null 2>&1
  sips -z 32 32     "$png" --out "$d/icon.iconset/icon_32x32.png"      >/dev/null 2>&1
  sips -z 32 32     "$png" --out "$d/icon.iconset/icon_16x16@2x.png"   >/dev/null 2>&1
  sips -z 16 16     "$png" --out "$d/icon.iconset/icon_16x16.png"      >/dev/null 2>&1
  iconutil --convert icns "$d/icon.iconset" --output "$icns" 2>&1
  rm -rf "$d"
}

make_icns "$SRC/terminal.png" "$SRC/terminal.icns"
cp "$SRC/terminal.icns" "$APPS/Open Terminal Here.app/Contents/Resources/applet.icns"

make_icns "$SRC/copy.png" "$SRC/copy.icns"
cp "$SRC/copy.icns" "$APPS/Copy Path.app/Contents/Resources/applet.icns"

make_icns "$SRC/pathbar.png" "$SRC/pathbar.icns"
cp "$SRC/pathbar.icns" "$APPS/Show Path Bar.app/Contents/Resources/applet.icns"

for a in "$APPS/Open Terminal Here.app" "$APPS/Copy Path.app" "$APPS/Show Path Bar.app"; do
  codesign --force --deep --sign - "$a" >/dev/null 2>&1
  touch "$a"
done

echo "icons applied and signed"
