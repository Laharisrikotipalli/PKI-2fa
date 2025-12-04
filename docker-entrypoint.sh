#!/usr/bin/env bash
set -euo pipefail

# Start cron if available
if command -v service >/dev/null 2>&1; then
  service cron start || true
elif command -v crond >/dev/null 2>&1; then
  crond || true
fi

sleep 1

# Run the Flask app as a module (ensures package-relative imports work)
exec python -m app.server
