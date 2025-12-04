#!/bin/sh
set -e

# Ensure cron files end with newline and have correct perms
if [ -d /etc/cron.d ]; then
  for f in /etc/cron.d/*; do
    [ -f "$f" ] || continue
    tail -c1 "$f" | read -r _ || echo >> "$f"
    chmod 0644 "$f"
  done
fi

# Start cron (daemonized)
service cron start || (crond -f &)

# Print cron status for debugging
echo "Cron started, listing /etc/cron.d:"
ls -la /etc/cron.d || true

# Start the web server (adjust command if you use uvicorn)
# Prefer uvicorn for FastAPI; for Flask use 'python -m server' or similar
if command -v uvicorn >/dev/null 2>&1; then
  echo "Starting uvicorn..."
  uvicorn app.main:app --host 0.0.0.0 --port 8080 &
else
  echo "Starting Flask via python -m server..."
  # ensure your server module is correct - replace 'server' if needed
  python -m server &
fi

# Tail logs so container keeps running
touch /var/log/cron.log /var/log/uvicorn.log /var/log/flask.log || true
tail -F /var/log/cron.log /var/log/uvicorn.log /var/log/flask.log &
wait
