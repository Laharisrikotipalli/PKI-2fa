# ============================
# STAGE 1 — BUILDER
# ============================
FROM python:3.11-slim AS build

WORKDIR /app

# Install build tools for cryptography
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ============================
# STAGE 2 — RUNTIME
# ============================
FROM python:3.11-slim AS runtime

WORKDIR /app

ENV TZ=UTC

# Install cron + timezone packages
RUN apt-get update && apt-get install -y \
    cron \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Set timezone to UTC
RUN ln -snf /usr/share/zoneinfo/UTC /etc/localtime && echo "UTC" > /etc/timezone

# Copy Python dependencies from build stage
COPY --from=build /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=build /usr/local/bin /usr/local/bin

# Copy application files
COPY . .

# Create volume mount points for seed + cron output
RUN mkdir -p /data && chmod 755 /data
RUN mkdir -p /cron && chmod 755 /cron

# Install cron job
COPY cronjob /etc/cron.d/cronjob
RUN chmod 0644 /etc/cron.d/cronjob
RUN crontab /etc/cron.d/cronjob

EXPOSE 8080

# Start cron service and API server
CMD service cron start && uvicorn main:app --host 0.0.0.0 --port 8080
