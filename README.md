# NatMEG BIDSifier - User Edition

A user-friendly interface for managing NatMEG data processing. Choose to run **locally** (no SSH required) or connect to a **remote server** via SSH tunnel.

## 30-Second Quick Start

1. `git clone <this-repo-url>`
2. `cd NatMEG-BIDSifier`
-----------------------------------

### On mac/linux
`make setup` - to setup repo

Choose your mode during setup:
- Local: Run app directly on your machine (no SSH required)
- Remote: Connect to remote server via SSH tunnel

`make ui` - to launch interactive menu (auto-detects your mode)

-----------------------------------
### On windows (normal computer)

Use Windows PowerShell or [Git Bash](https://git-scm.com/downloads) and run:

`./setup.sh` - to setup repo

Choose your mode during setup:
- Local: Run app directly on your machine (no SSH required)
- Remote: Connect to remote server via SSH tunnel

`./localctl-ui.sh` to launch interactive menu (auto-detects your mode)


## Use the application

![The NatMEG-BIDSifier browser](pics/config.png)

1. **Configuration**: Browse and load your configuration file or start from scratch
2. **Analyse / Editor**: Check and edit mis-spelled task names, modify runs etc. and save to a conversion table
3. **Execute**: Process the conversion table
4. **View the results**

## Common CL Tasks

### Universal (Works for Both Modes)
```bash
make ui              # Launch interactive menu (auto-detects your mode)
make update          # Get latest version
```

### Local Mode (No SSH)
```bash
make local-start     # Initialize local mode
make local-status    # Check if app is running
make local-stop      # Stop local mode
```

### Remote Mode (SSH Tunnel)
```bash
make start           # Launch a tunnel to the remote server
make stop            # Stop the tunnel
make status          # Check tunnel and server status
make list            # List all running servers
make cleanup-all     # Kill all your servers (with confirmation)
```

## Features

- **Two Modes:** 
  - **Local:** Run the app directly on your machine (no SSH required)
  - **Remote:** Connect to a remote server via SSH tunnel
- **Easy Setup:** One-time configuration wizard asking for your mode preference
- **Interactive Menu:** No command-line knowledge required
- **Auto-Port Selection:** Detects available ports automatically (remote mode)
- **Browser Integration:** Opens browser automatically (remote mode)
- **Safe Cleanup:** Only stops your own processes (remote mode)
- **Auto-Updates:** Stays synchronized with latest version

## Configuration

Settings are stored in `.config/settings` (created during setup).

### Local Mode
```bash
MODE="2"
LOCAL_PORT="8080"
```

### Remote Mode
```bash
MODE="1"
SSH_TARGET="youruser@compute.example.com"
REMOTE_REPO="/path/to/NatMEG-BIDSifier"
LOCAL_PORT="8080"
```

To reconfigure: `make setup`

## Installation for Administrators

### Option 1: Direct GitHub Clone
```bash
git clone git@github.com:k-CIR/NatMEG-BIDSifier.git
cd NatMEG-BIDSifier
make setup
```

### Option 2: Share via Filesystem
```bash
cp -r NatMEG-BIDSifier /shared/applications/
# Users: cd /shared/applications/NatMEG-BIDSifier && make setup
```

### Multiple Users on Shared Machine
```bash
sudo git clone git@github.com:k-CIR/NatMEG-BIDSifier.git /opt/natmeg-tunnel
sudo chmod 777 /opt/natmeg-tunnel/.config
# Each user runs: make setup
```

## How It Works

### Local Mode
```
Your Local Machine
  ├─ NatMEG Application (managed by make local-start)
  │  └─ FastAPI server on localhost:PORT
  └─ Browser
     └─ Accesses http://localhost:PORT
```
**How it works:**
- `make local-start` starts the NatMEG FastAPI server from `shared/admin/server`
- Dependencies installed automatically on first run (python -m pip install)
- Access the app at http://localhost:8080 in your browser
- Perfect for development, testing, or local data processing

### Remote Mode
```
┌─────────────────────────────────────────────────┐
│ Your Local Machine                              │
│ ┌────────────────────────────────────────────┐  │
│ │ Browser: localhost:PORT                    │  │
│ └────────────────────────────────────────────┘  │
│           ↑                                      │
│    SSH Tunnel (secure)                          │
│           ↓                                      │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ Remote Server                                   │
│ ┌────────────────────────────────────────────┐  │
│ │ NatMEG Application                          │  │
│ └────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```
Secure tunnel to a remote server. Requires SSH access and the app running on the remote host.

## Troubleshooting

### Local Mode Issues
| Problem | Solution |
|---------|----------|
| "Cannot connect to localhost:8080" | Run `make local-start` to start the app |
| "No module named 'uvicorn'" | Dependencies will install on first `make local-start` |
| "Permission denied" on dependencies | Automatic install uses `--break-system-packages` on macOS |
| App crashes on startup | Check log: `tail .connect_logs/local/.app.log` |
| Port 8080 already in use | Stop other services or use different port in setup |

### Remote Mode Issues
| Problem | Solution |
|---------|----------|
| SSH connection fails | Run `make setup` to reconfigure SSH details |
| Port already in use | Script auto-selects another port |
| Want to change server | Run `make setup` again |
| Permission denied when killing servers | Script only stops your own processes |
| Tunnel times out | Remote server may be down; contact admin |

### General
| Problem | Solution |
|---------|----------|
| Want latest version | Run `make update` |
| Want to switch modes | Run `make setup` to reconfigure |

## File Structure

```
NatMEG-BIDSifier/
├── localctl-ui.sh          # Interactive menu
├── setup.sh                # Setup wizard
├── Makefile                # Command shortcuts
├── README.md               # This file
├── .config/
│   └── settings            # Your configuration (created by setup)
├── scripts/
│   └── localctl.sh         # Main control script (synced from admin)
└── shared/
    └── admin/              # Admin repo (synced automatically)
```

## Advanced Usage

### Using localctl.sh Directly
For advanced users:

```bash
./scripts/localctl.sh --help
./scripts/localctl.sh start user@server /path/to/repo --local-port 9090
./scripts/localctl.sh cleanup --all user@server /path/to/repo
```

### Synchronization
The tool automatically stays synchronized with the admin repository. Updates flow through:

```
Admin Repo → Git Submodule → Symlink → Your Environment
                    (git pull and make update pulls latest)
```

## Support

- **Tunnel connection issues:** Check SSH configuration
- **Remote server issues:** Contact your NatMEG administrator
- **Tool issues:** Run `make help` or check documentation files in `.archive/`

## License

See the main NatMEG-BIDSifier repository for license information.
