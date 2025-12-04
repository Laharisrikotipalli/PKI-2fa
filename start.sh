#!/usr/bin/env bash
set -euo pipefail

# ensure python sees the installed packages
export PYTHONPATH=${PYTHONPATH:-/install}

# configure timezone (ensure /etc/localtime points to UTC)
ln -sf /usr/share/zoneinfo/UTC /etc/localtime || true
export TZ=UTC

# ensure directories exist
mkdir -p /data /cron
chmod 755 /data /cron

# If a crontab file is mounted at /cron/crontab, use that
# Else fallback to the app-provided crontab.txt
if [ -f /cron/crontab ]; then
  echo "Using crontab from /cron/crontab"
  crontab /cron/crontab
else
  echo "Using bundled crontab (/app/crontab.txt)"
  crontab /app/crontab.txt
fi

# Ensure cron is running (daemon)
# Start cron in background so we can run the app in foreground
cron

# Optionally, give a tiny delay to let cron start
sleep 1

# Start Flask app (keep in foreground)
# Use python -u to avoid buffering logs
exec python -u -m app.server
