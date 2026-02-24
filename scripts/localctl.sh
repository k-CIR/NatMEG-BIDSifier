#!/usr/bin/env bash
# Wrapper script for localctl that works cross-platform (including Windows Git Bash)
# This resolves the actual script location properly on all platforms

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ACTUAL_SCRIPT="$SCRIPT_DIR/../shared/admin/scripts/localctl.sh"

if [[ ! -f "$ACTUAL_SCRIPT" ]]; then
  echo "Error: Could not find localctl.sh at $ACTUAL_SCRIPT" >&2
  exit 1
fi

# Execute the actual script, passing all arguments
exec bash "$ACTUAL_SCRIPT" "$@"
