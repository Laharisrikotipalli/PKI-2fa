#!/bin/bash
set -euo pipefail

# Install the cron file into crontab if not already installed (idempotent)
if [ -f /etc/cron.d/2fa-cron ]; then
  # on many systems, cron reads /etc/cron.d automatically; ensure permissions are ok
  chmod 0644 /etc/cron.d/2fa-cron || true
fi

# Start cron daemon in background (try several fallbacks)
if command -v service >/dev/null 2>&1; then
  service cron start || true
elif [ -x /etc/init.d/cron ]; then
  /etc/init.d/cron start || true
elif command -v cron >/dev/null 2>&1; then
  cron || true
elif command -v crond >/dev/null 2>&1; then
  crond || true
else
  echo "Warning: cron binary not found; cron will not run"
fi

# Ensure /cron exists and is writable
mkdir -p /cron
touch /cron/last_code.txt || true
chmod 666 /cron/last_code.txt || true

# Optional: if your app expects the seed at /data/seed.txt, ensure /data exists
mkdir -p /data

# Exec the main process (the CMD). This ensures signals are forwarded.
exec "$@"
