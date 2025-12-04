# 🚀 PKI-Based Two-Factor Authentication (2FA) Microservice
**Built with Python, Flask, RSA-OAEP, TOTP, Cron & Docker**

A compact PKI-based 2FA microservice that:
- Decrypts an instructor-provided encrypted seed (RSA-OAEP)
- Generates and verifies TOTP codes (RFC 6238)
- Logs TOTP codes every minute via cron
- Persists seed and cron logs across container restarts

---
# 🚀 Running the Service
## 1. Build & Run (Docker Compose)
docker compose up -d --build

2. Health Check
curl http://localhost:8080/health

3. Generate TOTP
curl http://localhost:8080/generate-2fa

4. Verify TOTP
curl -X POST http://localhost:8080/verify-2fa \
  -H "Content-Type: application/json" \
  -d '{"totp":"123456"}'

# 🗂 Repository Layout
pki-2fa/
│── app/                     # Flask server & TOTP modules
│── cron/
│   └── 2fa-cron             # Cron schedule
│── scripts/
│   └── log_2fa_cron.py      # Cron logging script
│── keys/                    # Student + instructor RSA keys
│── Dockerfile
│── docker-compose.yml
│── encrypted_seed.txt
│── encrypted_commit_signature.txt
│── README.md

# 📌 Important Submission Files
File	Description
encrypted_seed.txt	Single-line base64 encrypted seed
encrypted_commit_signature.txt	Single-line base64 signature
keys/student_public.pem	Public key submitted to instructor
keys/student_private.pem	Required for decryption
GitHub repo URL & commit hash	Mandatory for submission

# 👩‍💻 Author
Lahari Sri
PKI–2FA Microservice Implementation

