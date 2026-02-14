#!/bin/bash

echo "Starting SMRITI OS..."

# ---------------- LOAD IR KEYMAP ----------------
sudo ir-keytable -c -p rc-6 -w /etc/rc_keymaps/tataplay.toml >/dev/null 2>&1

# ---------------- START YDOTOOL (Wayland input injector) ----------------
sudo pkill ydotoold 2>/dev/null

sudo ydotoold \
  --socket-path=/tmp/ydotool.socket \
  --socket-own=$(id -u):$(id -g) &

export YDOTOOL_SOCKET=/tmp/ydotool.socket
sleep 1

# ---------------- START REMOTE ENGINE ----------------
python3 /home/vinay/remote_engine.py &


# Wait for audio before launching browser
/home/vinay/wait_audio.sh

# ---------------- URLS ----------------
URL_HOME="file:///home/vinay/index.html"
URL_HOTSTAR="https://www.hotstar.com/in"
URL_YOUTUBE="https://www.youtube.com"

echo "Launching Chromium..."

exec chromium \
  --kiosk \
  --ozone-platform=wayland \
  --enable-features=UseOzonePlatform,OverlayScrollbar \
  --disable-pinch \
  --enable-webrtc-hide-local-ips-with-mdns=false \
  --overscroll-history-navigation=0 \
  --base-background-color=000000 \
  --no-first-run \
  --no-default-browser-check \
  --disable-infobars \
  --disable-session-crashed-bubble \
  --disable-translate \
  --disable-sync \
  --disable-extensions \
  --disable-background-networking \
  --disable-component-update \
  --disable-features=TranslateUI,OverscrollHistoryNavigation \
  --autoplay-policy=no-user-gesture-required \
  --ignore-gpu-blocklist \
  --enable-gpu-rasterization \
  --enable-zero-copy \
  --user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36" \
  --disable-features=KeyboardFocusableScrollers \
  --disk-cache-dir=/home/vinay/chrome-cache \
  --user-data-dir=/home/vinay/kiosk-profile \
  "$URL_HOME" "$URL_HOTSTAR" "$URL_YOUTUBE"
