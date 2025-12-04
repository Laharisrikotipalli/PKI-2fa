# Dockerfile (fixed and minimal for PKI-2FA)
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Install cron and required system deps (fixed the broken line)
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron openssl && \
    rm -rf /var/lib/apt/lists/*

# Copy project into image
COPY . /app

# Make sure pip is up-to-date and install python deps
RUN python -m pip install --upgrade pip setuptools wheel && \
    if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# If python3 command is missing, create a safe symlink to the working python
# (this makes scripts that call `python3` work)
RUN if ! command -v python3 >/dev/null 2>&1; then \
      ln -s "$(command -v python)" /usr/bin/python3 || true; \
    fi

# Expose the port we will run on
EXPOSE 8080

# Default command: run server using `python` (not python3)
CMD ["python", "app/server.py"]
