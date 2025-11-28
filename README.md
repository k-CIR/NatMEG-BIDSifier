# NatMEG-BIDSifier

## Overview

A toolkit for converting MEG/EEG data to BIDS (Brain Imaging Data Structure) format, developed at the NatMEG facility at Karolinska Institutet. The project supports a CLI and a web UI with remote connection, making it possible to edit your BIDS conversion and run it from a browser. It supports automated batch processing and includes features for data validation and quality checking.

## Features

- Convert MEG/EEG data to BIDS format
- Command-line interface for batch processing
- Automated metadata extraction and validation
- Web-based user interface for configuration and monitoring
- Remote job submission and real-time log streaming

## Installation

### Prerequisites

- Python 3.10 or higher
- Git

### Setup

1. Clone the repository:
```bash
git clone git@github.com:k-CIR/NatMEG-BIDSifier.git
cd NatMEG-BIDSifier
```

2. Install Python dependencies:
```bash
# create a venv and activate
python3 -m venv .venv
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
python bidsify.py --config config.yml [--analyse][--run][--report]
```
### Web application (FastAPI)

This repository also ships a small web application (FastAPI) that provides the same core conversion features as the desktop GUI but runs in a browser. The server is intentionally lightweight and is useful when you want to run conversions from a remote host, on a headless server, or inside a container.

Highlights
- Minimal FastAPI server located at `server/app.py` that runs `bidsify.py` for you.
- A small static front-end under `web/` implements a browser UI that speaks to the server via REST + WebSocket for real-time job logs.
- Web UI can submit jobs (analyse, run, report), stream logs in real-time, and fetch artifacts (e.g. `bids_results.json` or TSV conversion tables) produced by jobs.

Run the web server locally (recommended minimal steps):

```bash
# create a venv and activate
python3 -m venv .venv
source .venv/bin/activate

# install server dependencies (included in requirements.txt)
pip install -r requirements.txt

# run the FastAPI server (development)
uvicorn server.app:app --host 0.0.0.0 --port 8080
```

Open your browser at http://localhost:8080/ — the bundled web UI (in `web/index.html`) provides the same form-driven configuration and job panel that the desktop app used to provide.

Primary API endpoints (useful for automation)
- POST /api/analyze  -> runs bidsify --analyse with the provided config
- POST /api/run      -> runs bidsify --run
- POST /api/report   -> runs bidsify --report
- POST /api/jobs     -> create a job (returns job_id)
- GET  /api/jobs/{job_id}/artifacts -> list artifacts produced by a job
- POST /api/read-file -> read a file from the repository root (used by the UI to probe for `bids_results.json` etc.)

Real-time logs
- The server exposes real-time job logs via WebSockets at `ws://<host>/ws/jobs/{job_id}/logs` so the web UI can stream stdout/stderr while conversions run.

Security note
- The bundled server is optimised for convenience and internal/trusted use. If you expose the server publicly, add TLS and authentication and restrict file read/write operations as appropriate.

Quick .venv and local setup notes

macOS / Linux (recommended quick start)

1. Create a project virtual environment in the repository root and activate it (zsh / bash):

```bash
# create a .venv in the repo (place near project root so it's easy to ignore)
python3 -m venv .venv

# macOS / linux shells
source .venv/bin/activate
```

2. Install server deps and run the server:

```bash
pip install -r requirements.txt
uvicorn server.app:app --host 0.0.0.0 --port 8080
```

Windows (PowerShell)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r server/requirements.txt
py -3 -m uvicorn server.app:app --host 0.0.0.0 --port 8080
```

Tip: when running inside a container, bind 0.0.0.0 so the host can reach the app. For production you should run the server behind TLS and implement an authentication layer and file access restrictions.

Testing the local web UI

After the server is running, open http://localhost:8080/ in a browser to use the web UI. You can submit jobs via the UI or call the API endpoints from other automation scripts.

Developer notes

- The `web/` folder contains a lightweight static UI which the server serves for convenience in development. In production you can serve this static UI separately.
- The server runs `bidsify.py` under the same repo; it will use the Python interpreter inside the active `.venv` unless overridden by `PYTHON` env var.

## Configuration

Copy `default_config.yml` and customize it for your dataset:

```yaml
# Configuration example
dataset_name: "MyStudy"
output_directory: "/path/to/output"
# ... additional settings
```

## Project Structure

```
├── bidsify.py              # Main conversion script
├── requirements.txt        # Python dependencies
├── default_config.yml      # Default configuration
└── electron/              # (moved to feature/electron-app branch)
    ├── main.js            # Electron main process
    ├── renderer.js        # UI logic
    ├── package.json       # Node.js dependencies
    └── resources/         # Bundled Python environment
```

## Development

### Building the Electron App

```bash
cd electron
npm run build           # Build for current platform
npm run build:mac       # Build for macOS
npm run build:win       # Build for Windows
npm run build:linux     # Build for Linux
```

## Dependencies

### Core Libraries
- MNE-Python (>=1.5.0) - MEG/EEG data processing
- MNE-BIDS (>=0.13.0) - BIDS conversion
- NumPy, SciPy, Pandas - Scientific computing
- PyQt6 - GUI components

See `requirements.txt` for complete list.

## License

MIT

## Authors

NatMEG - Karolinska Institutet

## Acknowledgments

This tool is built on top of MNE-Python and MNE-BIDS projects.
