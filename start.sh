#!/bin/bash
# /app/start.sh

# --- 1. SETUP & UTILITIES ---

# Ensure the directory for the cron output file exists and has correct permissions
# The submission requires the log at /cron/last_code.txt
mkdir -p /cron
touch /cron/last_code.txt
chmod 666 /cron/last_code.txt

# Run the crontab installation command if necessary (though your Dockerfile handles it, 
# this can be a safeguard if you were using an actual crontab file instead of /etc/cron.d)
# Since you used /etc/cron.d, the schedule is ALREADY installed by the Dockerfile.

# --- 2. START BACKGROUND SERVICES (CRON) ---

echo "Starting cron daemon..."
# Start the cron daemon in the background
# The '-L' flag is often used to specify a log file if not logging to stdout/stderr
cron

# Optional: Verify cron jobs are loaded (check inside running container)
# crontab -l

# --- 3. START FOREGROUND APPLICATION (WEB SERVER) ---

echo "Starting Flask web server..."
# Run the main Flask application. 
# Using 'exec' replaces the current shell with the python process, 
# making the web server the primary process, which is ideal for Docker.
exec python -m app.server

# The container will stay alive as long as 'app.server' is running.