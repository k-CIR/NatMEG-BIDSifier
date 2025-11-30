# NatMEG-BIDSifier

## Overview

A toolkit for converting MEG/EEG data to BIDS (Brain Imaging Data Structure) format, developed at the NatMEG facility at Karolinska Institutet. The project supports a CLI and a web UI with remote connection, making it possible to edit your BIDS conversion and run it from a browser. It supports automated batch processing and includes features for data validation and quality checking.

## Features

- Convert MEG/EEG data to BIDS format
- Command-line interface for batch processing
- Automated metadata extraction and validation
- Web-based user interface for configuration and monitoring
- Remote job submission and real-time log streaming

## Installation (on server or local)

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

### Command Line (on server)

```bash
python bidsify.py --config config.yml [--analyse][--run][--report]
```
### Web application (FastAPI)

This repository also have a small web application (FastAPI) that allows user-friendly local configuration and edits to allow remote BIDS batch processing on a server.

### Quick remote access: one-liner alias ("cir-bidsify")
For a convenient, interactive helper we include `scripts/cir-bidsify.sh` in the repo. It implements a safe start/stop/status workflow and avoids the typical race conditions when starting the remote server and opening a background tunnel.

#### Prerequisites (local)

- scripts/cir-bidsify.sh
- remote machine with SSH access and full NatMEG-BIDSifier installed

### Start web-based BIDSifier on remote server with port forwarding
```shell
./scripts/cir-bidsify.sh user@server /server/path/to/NatMEG-BIDSifier
```

Usage examples

```bash
# interactive prompt for target and repo
./scripts/cir-bidsify.sh

# provide target and repo path
./scripts/cir-bidsify.sh <user>@<server> /server/path/to/script

# start with autossh (auto-reconnect)
./scripts/cir-bidsify.sh <user>@<server> /server/path/to/script --autossh

# stop the tunnel and optionally the remote server
./scripts/cir-bidsify.sh stop <user>@<server> /server/path/to/script

# check status
./scripts/cir-bidsify.sh status <user>@<server> /server/path/to/script
```

#### Setting up an alias

Recommended alias (safe): use the script or the already documented wait-for-ping one-liner. Example alias that calls the helper script:

Add this to your `~/.bashrc` / `~/.zshrc` (replace `<user>` and `/server/path/to/NatMEG-BIDSifier`):

```bash
alias cir-bidsify="./scripts/cir-bidsify.sh user@server /server/path/to/NatMEG-BIDSifier"
```

Now open `http://localhost:8080`!

Highlights
- Minimal FastAPI server located at `server/app.py` that runs `bidsify.py` for you.
- A small static front-end under `web/` implements a browser UI that speaks to the server via REST + WebSocket for real-time job logs.
- Web UI can submit jobs (analyse, run, report), stream logs in real-time, and fetch artifacts (e.g. `bids_results.json` or TSV conversion tables) produced by jobs.

See (scripts/README.md)[scripts/README.md] for full details of the helper scripts to start/stop the server and create SSH tunnels.


Recommended alias (safe): use the script or the already documented wait-for-ping one-liner. Example alias that calls the helper script:

```bash
alias cir-bidsify='$PWD/scripts/cir-bidsify.sh <user>@<server> /server/path/to/script'
```

Now open `http://localhost:8080`!

Real-time logs
- The server exposes real-time job logs via WebSockets at `ws://<host>/ws/jobs/{job_id}/logs` so the web UI can stream stdout/stderr while conversions run.

Security note
- The bundled server is optimised for convenience and internal/trusted use. If you expose the server publicly, add TLS and authentication and restrict file read/write operations as appropriate.

### Quick .venv and local setup notes (local development or single-host use)

#### macOS / Linux (recommended quick start)

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
uvicorn server.app:app --host 127.0.0.1 --port 8080
```

#### Windows (PowerShell)

TBA


### Developer notes

- The `web/` folder contains a lightweight static UI which the server serves for convenience in development. In production you can serve this static UI separately.
- The server runs `bidsify.py` under the same repo; it will use the Python interpreter inside the active `.venv` unless overridden by `PYTHON` env var.

## Configuration

Copy `default_config.yml` and customize it for your parameters:

```yaml
# Configuration example
dataset_name: "MyStudy"
output_directory: "/path/to/output"
# ... additional settings
```

## Project structure

Top-level layout you will interact with during development / server runs:

```
├── bidsify.py            # Main conversion CLI
├── requirements.txt      # Python dependencies (includes server deps)
├── default_config.yml    # Default conversion configuration
├── server/               # FastAPI app and server utilities
│   ├── app.py            # FastAPI app (REST + WebSocket + job runner)
│   └── ...
├── web/                  # Static frontend served by the FastAPI server
│   ├── index.html
│   ├── app-config.js
│   ├── app-jobs.js
│   ├── app-editor.js
│   └── styles.css
├── scripts/              # helper scripts for server / tunnelling
│   └── serverctl.sh      # start/stop/status helper (uses .server.pid + ~/natmeg-server.log)
│   └── cir-bidsify.sh      # helper to connect and start remote server with port forwarding
└── ...

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

[Andreas Gerhardsson]([agerhardsson](https://github.com/agerhardsson)) - NatMEG - Karolinska Institutet

## Acknowledgments

This tool is built on top of MNE-Python and MNE-BIDS projects.
