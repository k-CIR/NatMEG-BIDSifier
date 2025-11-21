# Packaging and X11 (Linux)

This document explains how to run the Electron GUI on headless Linux hosts using Xvfb and how to build Linux installers (.AppImage/.deb) using `electron-builder`.

## Run on a headless server (Xvfb)

Install Xvfb (Ubuntu/Debian):

```bash
sudo apt update && sudo apt install -y xvfb
```

Use the included helper to run the app under Xvfb:

```bash
cd electron
bash ./launch-with-xvfb.sh
```

The wrapper uses `xvfb-run` to create a temporary virtual X server and then runs `npm run start` inside it.

If you want to run with custom screen resolution:

```bash
SCREEN_RES=1920x1080x24 bash ./launch-with-xvfb.sh
```

Alternatively, start the app directly under Xvfb using the system `xvfb-run` tool:

```bash
xvfb-run -s "-screen 0 1600x1200x24" npm run start
```

> Tip: You can also use a remote VNC server connected to the Xvfb instance (e.g., x11vnc) for interactive access.

## Headless flags

You can start the app with `--headless` or set environment variables `NATMEG_HEADLESS=1` or `NATMEG_NO_GPU=1` to apply recommended flags for headless/VM environments. This will disable the GPU and hardware acceleration in Electron.

Example:

```bash
npm start -- --headless
# or
NATMEG_HEADLESS=1 npm start
```

## Build Linux packages

Electron packaging is handled by `electron-builder`. The `package.json` includes convenient scripts:

- Build both AppImage and deb: `npm run build:linux`
- Build only AppImage: `npm run build:linux:appimage`
- Build only deb: `npm run build:linux:deb`
- Convenience build script: `npm run pack:linux` (runs `build:linux` and prints the output path)

Build prerequisites:

- Node 18+ / npm
- libgtk and other desktop dependencies (for headless container builds you may need to install extra libraries)

On Ubuntu/Debian you'll commonly need:

```bash
sudo apt install -y libgtk-3-0 libnotify4 libnss3 libxss1 libasound2 libxtst6 libx11-6
```

The built artifacts will be in `electron/dist/`.

Note: the build now bundles `bidsify.py`, `default_config.yml` and `requirements.txt` into the app resources so the GUI can execute the Python backend in packaged apps. The NatMEG/CIR logos are also included so `index.html` logos are available in the macOS and Linux builds.
### GitHub Actions example (builds AppImage + deb without Docker)

Add the `.github/workflows/build-linux.yml` workflow to automatically build both AppImage and `.deb` packages on each push to `main` or pull request. The workflow runs on `ubuntu-latest` and uses `actions/setup-node@v4` with Node 18.

Artifacts built by the workflow are stored in `electron/dist` and uploaded into the workflow run artifacts (downloadable from the Actions UI).

### noVNC + Systemd

If you need browser-based remote access to the GUI via noVNC, install `x11vnc`, `websockify`, and `novnc` and use the helper `packaging/start-novnc.sh`. This script launches Xvfb on a virtual display, runs `x11vnc` to serve that display, and uses `websockify` to expose the VNC port via WebSockets to `noVNC`.

Install dependencies for noVNC on Debian/Ubuntu:

```bash
sudo apt install -y x11vnc websockify novnc
```

Then start the stack:

```bash
cd packaging
bash start-novnc.sh
```

noVNC will be reachable on http://<server-ip>:6080 by default.

To make the GUI start automatically on boot and attach to a display, create a systemd service using `packaging/systemd/natmeg-bidsifier.service` and `systemctl enable natmeg-bidsifier@<username>.service`.

### Building on Ubuntu/Debian (example)

1. Install system deps:

```bash
sudo apt update
sudo apt install -y nodejs npm libgtk-3-0 libnotify4 libnss3 libxss1 libasound2 libxtst6 libx11-6
```

2. Install project dependencies and prepare build:

```bash
cd electron
npm ci
```

3. Build packages (AppImage + deb):

```bash
npm run build:linux
```

You can also build only the AppImage or only the deb using `npm run build:linux:appimage` or `npm run build:linux:deb`.

### .desktop template

Create a desktop launcher for your installed app (useful after installing `.deb` or unpacking AppImage):

```
[Desktop Entry]
Name=NatMEG BIDSifier
Exec=/opt/NatMEG-BIDSifier/NatMEG-BIDSifier %U
Icon=/opt/NatMEG-BIDSifier/resources/icon.png
Type=Application
Categories=Science;Education;
Terminal=false
```

Adjust `Exec` and `Icon` paths based on where the .deb placed the files (the .deb typically installs into /opt or /usr/local).

### Installing packages

After building the `.deb`, you can install it with:

```bash
sudo dpkg -i electron/dist/NatMEG-BIDSifier*.deb
sudo apt-get install -f  # fix dependencies if dpkg reported missing packages
```

The AppImage can be made executable and run directly:

```bash
chmod +x electron/dist/NatMEG-BIDSifier-*.AppImage
./electron/dist/NatMEG-BIDSifier-*.AppImage
```

## Systemd service example (CLI-only)
If you want to run the CLI part (`bidsify.py`) on a server without the GUI, create a systemd service that calls the Python script directly:

```
[Unit]
Description=NatMEG BIDS conversion service
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/NatMEG-BIDSifier
ExecStart=/usr/bin/python3 /path/to/NatMEG-BIDSifier/bidsify.py --config /path/to/config.yml
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

## Troubleshooting

- If the AppImage does not launch on your server, try running with `--no-sandbox` or `--disable-gpu` environment variables.
- Use `xvfb-run` logs to check if Xvfb fails to allocate a display.
 - Packaging failures often relate to missing dependencies (GTK libraries) in the build environment; ensure your build host has the required libraries installed.

If you'd like help creating a reproducible build environment without Docker (for example, a VM image or a script that installs native build dependencies), tell me which distribution you plan to use and I’ll provide tailored steps. You can also use the included `packaging/install_deps_ubuntu.sh` script to quickly provision a Ubuntu host.
