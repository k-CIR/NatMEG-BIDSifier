# NatMEG-BIDSifier

A toolkit for converting MEG/EEG data to BIDS (Brain Imaging Data Structure) format, developed for the NatMEG facility at Karolinska Institutet. The project supports a CLI and a web UI; an Electron desktop app historically existed but has been moved to a separate branch to keep this branch lightweight.

## Overview

NatMEG-BIDSifier provides both a command-line interface and an Electron-based GUI for converting neuroimaging data to BIDS format. It supports automated batch processing and includes features for data validation and quality checking.

## Features

- Convert MEG/EEG data to BIDS format
- Desktop GUI built with Electron
- Command-line interface for batch processing
- Support for multiple data formats (via MNE-Python)
- Automated metadata extraction and validation
- BIDS validator integration
- Handles noise recordings, head position files, and anatomical data

## Installation

### Prerequisites

- Python 3.10 or higher
    <!-- Electron packaging moved to `feature/electron-app` branch -->
- Git

### Setup

1. Clone the repository:
```bash
git clone git@github.com:k-CIR/NatMEG-BIDSifier.git
cd NatMEG-BIDSifier
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. For the Electron GUI:
```bash
cd electron
npm install
./setup_python_env.sh
```

## Usage

### Command Line

```bash
python bidsify.py --config config.yml [--analyse]
```

### Desktop Application

The Electron-based desktop app has been moved out of this branch to keep the main branch small and focused on the command-line and web interfaces.

If you still need the full Electron sources and build artifacts, use the `feature/electron-app` branch which contains the Electron project and packaging scripts. This branch keeps the main repo small and avoids checking in large binary artifacts.

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
