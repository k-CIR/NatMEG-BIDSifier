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
