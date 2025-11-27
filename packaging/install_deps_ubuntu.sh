#!/usr/bin/env bash
# Install runtime and build dependencies on Debian / Ubuntu for NatMEG-BIDSifier

set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "Please run as root or sudo" >&2
    exit 1
fi

echo "Updating apt and installing core packages..."
apt update
apt install -y curl gnupg apt-transport-https ca-certificates

echo "Installing Node.js 18 (NodeSource)..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs build-essential

echo "Installing Electron build / runtime deps"
apt install -y libgtk-3-0 libnotify4 libnss3 libxss1 libasound2 libxtst6 libx11-6 xvfb x11vnc websockify

echo "Optional: install noVNC (system package may be novnc or novnc-gtk depending on distribution)"
if ! command -v websockify >/dev/null 2>&1; then
  echo "websockify not found. You may need to 'apt install websockify' or install novnc from source." >&2
fi

if [ -d "$(pwd)/electron" ]; then
  echo "Installing project npm deps for electron"
  cd electron
  npm ci
else
  echo "Electron project not present in this branch. Switch to 'feature/electron-app' to install electron packaging dependencies." >&2
fi

echo "Done. If you need to run GUI packaging scripts, switch to the 'feature/electron-app' branch which contains the electron project and packaging artifacts."
