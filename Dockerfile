# Stage 1: Builder - install Python packages into /install
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build deps used by some packages (cryptography etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    cargo \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file and install to /install for copying into runtime
COPY requirements.txt /build/requirements.txt
RUN python -m pip install --upgrade pip \
 && python -m pip install --no-cache-dir --target /install -r /build/requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Ensure cron and proc tools are available (procps provides ps/pgrep)
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron procps \
    && rm -rf /var/lib/apt/lists/*

# Set timezone to UTC
RUN ln -sf /usr/share/zoneinfo/UTC /etc/localtime

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /install /install
ENV PYTHONPATH=/install

# Copy application code
COPY . /app

# Ensure your scripts are executable
RUN chmod +x /app/scripts/*.py || true \
 && chmod +x /app/start.sh 2>/dev/null || true \
 && chmod +x /app/docker-entrypoint.sh 2>/dev/null || true

# Install cron job file from repo into /etc/cron.d
# This expects cron/2fa-cron to exist in your repo (assignment required)
COPY cron/2fa-cron /etc/cron.d/2fa-cron
RUN chmod 0644 /etc/cron.d/2fa-cron \
 && touch /var/log/cron.log

# Expose the server port (adjust if your app uses a different port)
EXPOSE 8080

# Use an entrypoint script to start cron then the app
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT [ "/usr/local/bin/docker-entrypoint.sh" ]

# Default command: start your app. Adjust if your app uses uvicorn/gunicorn.
CMD ["python3", "/app/app.py"]
