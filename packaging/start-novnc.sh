#!/usr/bin/env bash
# Start Xvfb, the electron app and expose the X session through noVNC (websockify)

set -euo pipefail

XVFB_SCREEN=${XVFB_SCREEN:-99}
XVFB_RES=${XVFB_RES:-1280x800x24}
DISPLAY=:$XVFB_SCREEN
export DISPLAY

if ! command -v Xvfb >/dev/null 2>&1; then
  echo 'ERROR: Xvfb is required. Install: sudo apt install xvfb' >&2
  exit 2
fi
if ! command -v x11vnc >/dev/null 2>&1; then
  echo 'ERROR: x11vnc is required. Install: sudo apt install x11vnc' >&2
  exit 2
fi
if ! command -v websockify >/dev/null 2>&1; then
  echo 'ERROR: websockify is required by noVNC. Install: sudo apt install websockify' >&2
  exit 2
fi

echo "Launching Xvfb on display $DISPLAY ($XVFB_RES)"
Xvfb $DISPLAY -screen 0 $XVFB_RES &
XVFB_PID=$!

sleep 0.5

echo "Launching x11vnc on $DISPLAY"
x11vnc -display $DISPLAY -nopw -forever &
X11VNC_PID=$!

sleep 0.5

NO_VNC_PORT=${NO_VNC_PORT:-6080}
echo "Starting websockify to expose VNC on :$NO_VNC_PORT"
websockify --web=/usr/share/novnc $NO_VNC_PORT localhost:5900 &
WEBSOCKIFY_PID=$!

sleep 0.5

echo "Starting NatMEG-BIDSifier"
cd $(dirname "$0")/../electron || cd electron
npm run start -- --headless &
APP_PID=$!

echo "Started processes: Xvfb=$XVFB_PID x11vnc=$X11VNC_PID websockify=$WEBSOCKIFY_PID app=$APP_PID"

wait $APP_PID || exit $?
