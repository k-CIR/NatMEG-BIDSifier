Server control scripts
======================

This directory contains a small helper script to start/stop the local FastAPI / Uvicorn server used by the project.

serverctl.sh
-----------

Usage:

  ./serverctl.sh start    # start uvicorn in background using .venv python (writes .server.pid)
  ./serverctl.sh status   # check pidfile and whether server is running
  ./serverctl.sh stop     # stop server started via this script
  ./serverctl.sh restart  # restart

Notes:
- The script prefers the Python interpreter in `.venv/bin/python` if present.
- Server logs are written to `~/natmeg-server.log` by default.
- The script refuses to start if port 8080 is already bound (helps avoid collisions).
- You can override host/port per-user via environment or flags:
  - Example: `PORT=18080 ./scripts/serverctl.sh start`
  - Or: `./scripts/serverctl.sh start --port 18080 --host 127.0.0.1`


# Start remote server on a custom port per-user, and tunnel to local 8080
./scripts/cir-bidsify.sh start user@server /path/to/NatMEG-BIDSifier --remote-port 18080 --local-port 8080
cir-bidsify.sh
---------------

`cir-bidsify.sh` is a convenient helper that combines three common steps when you want to run the FastAPI server on a remote host and access it locally via a secure SSH tunnel:

- ensure the remote server is started (uses `./scripts/serverctl.sh start` on the remote repo)
- wait for the remote server to respond to `/api/ping` (sanity/health check)
- create a local SSH tunnel that forwards remote localhost:REMOTE_PORT to your laptop localhost:LOCAL_PORT

**Multi-user support**: By default, the script automatically selects a free remote port (18080-18150) and a free local port, allowing multiple users to run servers concurrently on shared hosts without conflicts. Connection details are saved locally so you can run `status`, `stop`, `list`, and `cleanup` commands without re-specifying host and path.

Behavior and files
- Writes the background tunnel PID to `.tunnel.pid` in the repository root on your local machine.
- Saves the auto-selected remote port to `.tunnel.port` for reuse in status/stop commands.
- Saves SSH target and remote repo path to `.tunnel.repo` for simplified subsequent commands.
- By default uses auto-port selection (remote: 18080-18150, local: 8080+). Override with `--remote-port` to pick a specific port.
- The script supports password-less SSH (preferred). If a key is not available and `sshpass` is installed it will prompt once for a password and use `sshpass` to avoid multiple prompts. Otherwise it will fall back to interactive SSH.
- Cross-platform local port detection works on macOS, Linux, and Windows (Git Bash).

Usage
```
./scripts/cir-bidsify.sh [start|stop|status|list|cleanup] [user@host] [remote_repo] [--local-port N] [--remote-port N] [--autossh]
```

Commands:
- `start` (default): starts remote server with auto-port, waits for ping, creates local tunnel (auto-stops any previous tunnel first)
- `status`: print local tunnel state and query `serverctl.sh status` on the remote host
- `stop`: stop local tunnel (kills PID in `.tunnel.pid`) and optionally stop the remote server
- `list`: list all your running uvicorn servers on the remote host
- `cleanup`: stop a specific server by port number (useful when pidfile is missing)

Flags and common examples
- `--local-port N`: port on your laptop to listen on (defaults to 8080, auto-picks if busy)
- `--remote-port N`: remote server's loopback port (disables auto-port, uses specified port)
- `--autossh`: use `autossh` (recommended for auto-reconnect) instead of a plain `ssh` tunnel. `autossh` must be installed on your laptop.

Examples
```
# Start with auto-port (simplest, recommended for multi-user environments)
./scripts/cir-bidsify.sh andrge@compute.kcir.se /data/users/natmeg/scripts/NatMEG-BIDSifier

# After running start once, you can use simplified commands
./scripts/cir-bidsify.sh status
./scripts/cir-bidsify.sh list
./scripts/cir-bidsify.sh stop

# Start with specific remote port (disables auto-port)
./scripts/cir-bidsify.sh andrge@compute.kcir.se /data/users/natmeg/scripts/NatMEG-BIDSifier --remote-port 18090

# Start with autossh for auto-reconnect
./scripts/cir-bidsify.sh andrge@compute.kcir.se /data/users/natmeg/scripts/NatMEG-BIDSifier --autossh

# Clean up orphaned server on a specific port
./scripts/cir-bidsify.sh cleanup
# (prompts for port number)
```

Exit codes
- 0: success
- 1..6: heterogeneous failure codes (see script output). Typical failures include authentication issues, timeout waiting for remote `/api/ping`, missing `autossh` when requested, or local port conflicts.

Security / notes
- The script prefers the remote server to bind to the remote host's loopback (127.0.0.1). This is safer because the tunnel forwards the service back to your laptop instead of exposing the server to the public internet.
- Use SSH key authentication for unattended runs; otherwise consider `sshpass` if you want to automate password entry (it has security tradeoffs).
- The script writes a local `.tunnel.pid` file. If you remove or accidentally delete the pidfile you'll need to stop the background tunnel manually (kill the ssh/autossh PID).

If you want, we can add unit tests or a small integration test (using a local dummy server) to validate this helper on CI; open a follow-up issue or tell me to implement it.
