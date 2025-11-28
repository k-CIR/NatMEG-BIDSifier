#!/usr/bin/env bash
# Lightweight server control script for NatMEG-BIDSifier
# Usage: ./serverctl.sh start|stop|status|restart

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PIDFILE="$REPO_ROOT/.server.pid"
LOGFILE="$HOME/natmeg-server.log"
# Prefer the repo venv python, but fall back to system python
PY="$REPO_ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  PY="$(command -v python 2>/dev/null || true)"
fi

PORT=8080

is_port_in_use(){
  # returns 0 if port bound, non-zero otherwise
  if command -v lsof >/dev/null 2>&1; then
    lsof -nP -iTCP:${PORT} -sTCP:LISTEN >/dev/null 2>&1 && return 0 || return 1
  fi
  # fallback: try netstat
  if command -v netstat >/dev/null 2>&1; then
    netstat -an | grep "LISTEN" | grep -q ":${PORT} " && return 0 || return 1
  fi
  return 1
}

start(){
  if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE" 2>/dev/null || echo '')
    if [ -n "$PID" ] && kill -0 "$PID" >/dev/null 2>&1; then
      echo "Server appears to already be running (pid=$PID)"; return 0
    else
      echo "Removing stale pidfile"; rm -f "$PIDFILE"
    fi
  fi

  if is_port_in_use; then
    echo "Port $PORT is already in use — aborting start"; return 1
  fi

  if [ -z "$PY" ]; then
    echo "No python runtime found; cannot start server"; return 2
  fi

  echo "Starting NatMEG server using $PY (port $PORT)";
  nohup "$PY" -m uvicorn server.app:app --host 127.0.0.1 --port $PORT > "$LOGFILE" 2>&1 &
  NEWPID=$!
  echo "$NEWPID" > "$PIDFILE"
  echo "server started (pid=$NEWPID), logs -> $LOGFILE"
}

stop(){
  if [ ! -f "$PIDFILE" ]; then
    echo "No pidfile found — server probably not started by this script"; return 0
  fi
  PID=$(cat "$PIDFILE" 2>/dev/null || echo '')
  if [ -z "$PID" ]; then
    echo "Empty pidfile; removing"; rm -f "$PIDFILE"; return 0
  fi
  if kill -0 "$PID" >/dev/null 2>&1; then
    echo "Stopping server pid=$PID"; kill "$PID" || true
    sleep 0.5
    if kill -0 "$PID" >/dev/null 2>&1; then
      echo "Process still alive; sending TERM"; kill -TERM "$PID" || true
    fi
  else
    echo "No such process $PID (stale pidfile), cleaning up";
  fi
  rm -f "$PIDFILE"
}

status(){
  if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE" 2>/dev/null || echo '')
    if [ -n "$PID" ] && kill -0 "$PID" >/dev/null 2>&1; then
      echo "NatMEG server running (pid=$PID)"; return 0
    else
      echo "Pidfile exists but process not running (pid=$PID)"; return 1
    fi
  fi
  if is_port_in_use; then
    echo "Port $PORT is in use by another process (server might've been started outside this script)"; return 0
  fi
  echo "NatMEG server not running"; return 3
}

case "${1:-}" in
  start) start ;; 
  stop) stop ;; 
  restart) stop; sleep 0.4; start ;; 
  status) status ;; 
  *)
    echo "Usage: $0 {start|stop|status|restart}"; exit 2
    ;;
esac
