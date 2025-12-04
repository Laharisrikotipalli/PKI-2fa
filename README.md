# 🚀 PKI-Based Two-Factor Authentication (2FA) Microservice
**Built with Python, Flask, RSA-OAEP, TOTP, Cron & Docker**

A compact PKI-based 2FA microservice that:
- Decrypts an instructor-provided encrypted seed (RSA-OAEP)
- Generates and verifies TOTP codes (RFC 6238)
- Logs TOTP codes every minute via cron
- Persists seed and cron logs across container restarts

---

## Quick Start

1. Build & run:
```bash
docker compose up -d --build

2. Health check:
curl http://localhost:8080/health

3. Generate TOTP:
curl http://localhost:8080/generate-2fa

4. Verify TOTP:
curl -X POST http://localhost:8080/verify-2fa \
  -H "Content-Type: application/json" \
  -d '{"totp":"123456"}'






## Repo layout

app/                 # server and TOTP modules
cron/2fa-cron        # cron schedule
scripts/log_2fa_cron.py
keys/                # instructor + student keys (required)
Dockerfile
docker-compose.yml
encrypted_seed.txt
encrypted_commit_signature.txt
README.md

Important files to submit :
encrypted_seed.txt (single-line base64)
encrypted_commit_signature.txt (single-line base64)
keys/student_public.pem
keys/student_private.pem (required by assignment)
GitHub repo URL & commit hash

Author
Lahari Sri
