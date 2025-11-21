#!/usr/bin/env bash
# Launch NatMEG-BIDSifier inside Xvfb so GUI can start on headless servers
# Usage: ./launch-with-xvfb.sh [--args] (it will forward to npm start)

set -euo pipefail

XVFB_CMD=${XVFB_CMD:-xvfb-run}
SCREEN_RES=${SCREEN_RES:-1600x1200x24}

if ! command -v "$XVFB_CMD" >/dev/null 2>&1; then
  echo "ERROR: $XVFB_CMD not found. Install with: sudo apt install xvfb" >&2
  exit 2
fi

echo "Starting NatMEG-BIDSifier under Xvfb ($SCREEN_RES)"
exec "$XVFB_CMD" -s "-screen 0 $SCREEN_RES" -- "npm" "run" "start" "$@"
