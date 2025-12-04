🚀 PKI-Based Two-Factor Authentication (2FA) Microservice
Built with Python, Flask, RSA-OAEP, TOTP, Cron & Docker

This project implements a fully secure Public Key Infrastructure (PKI) based Two-Factor Authentication (2FA) microservice.
It supports RSA-OAEP encrypted seed decryption, TOTP generation, 2FA verification, cron-based logging, and persistent secure storage — all inside a Docker container.

This microservice is designed according to the official assignment specification and meets all functional and security requirements.

📌 Features
🔐 1. RSA-OAEP Seed Decryption

Accepts an encrypted seed from instructor API

Decrypts using student_private.pem

Persists decrypted seed securely to /app/keys/seed.txt

⏱ 2. TOTP Generation

Implements RFC 6238

Generates 6-digit time-based codes every 30 seconds

Uses SHA-1 hashing as required

🧪 3. TOTP Verification

Validates user-provided TOTP code

Supports ±1 time-step clock drift

🕒 4. Cron-Based Code Logging

Every 1 minute, a cron job generates the current TOTP code

Logs results to /app/cron/last_code.txt

Demonstrates correct cron scheduling inside Docker

📦 5. Fully Containerized

Runs on Python 3.11 Slim

Exposes microservice API on port 8080

Uses Docker volume for seed persistence after container restarts

🗂 Repository Structure

pki-2fa/
│── Dockerfile
│── docker-compose.yml
│── README.md
│── requirements.txt
│── encrypted_seed.txt
│── encrypted_commit_signature.txt
│
├── app/
│   ├── server.py
│   ├── decrypt_seed.py
│   ├── generate_totp.py
│   ├── verify_totp.py
│   └── __init__.py
│
├── keys/
│   ├── instructor_public.pem
│   ├── student_public.pem
│   └── student_private.pem
│
├── cron/
│   └── 2fa-cron
│
└── scripts/
    └── log_2fa_cron.py

🧩 API Endpoints
1. Health Check
GET /health


Returns:

{ "service": "pki-2fa", "status": "ok" }

2. Decrypt Seed
POST /decrypt-seed


Request body:

{ "encrypted_seed": "<base64-seed>" }


Successful response:

{ "status": "ok", "message": "Seed decrypted and persisted" }

3. Generate 2FA Code
GET /generate-2fa


Response:

{ "totp": "123456" }

4. Verify 2FA Code
POST /verify-2fa


Body:

{ "totp": "123456" }


Response (valid):

{ "valid": true }


Response (invalid):

{ "valid": false }

🧱 Docker Setup
Build & Start
docker compose up -d --build

Check logs:
docker compose logs --tail=100

Test the API:
curl http://localhost:8080/health
curl http://localhost:8080/generate-2fa

🕒 Cron Job

Cron file (cron/2fa-cron):

* * * * * root cd /app && /usr/local/bin/python3 scripts/log_2fa_cron.py >> /app/cron/last_code.txt 2>&1


To verify cron output:

docker exec -it <container> tail -n 20 /app/cron/last_code.txt

🔑 Key Files
File	Purpose
student_private.pem	Required for decrypting the seed & signing commit hash
student_public.pem	Submitted to the instructor
instructor_public.pem	Used to encrypt commit signature

⚠️ These keys are for assignment use only and must not be reused elsewhere.

📝 Submission Artifacts

Your repo contains all required files:

encrypted_seed.txt (single-line base64 string)

encrypted_commit_signature.txt

keys/student_public.pem

keys/student_private.pem (required by assignment)

Full source code

Dockerfile + docker-compose.yml

Cron configuration

✔️ How to Verify Before Submission

Run:

curl http://localhost:8080/health
curl http://localhost:8080/generate-2fa
curl -X POST http://localhost:8080/verify-2fa -d '{"totp":"123456"}' -H "Content-Type: application/json"


Check cron:

docker exec -it $(docker ps -q) tail -n 20 /app/cron/last_code.txt


Restart test:

docker compose restart
curl http://localhost:8080/generate-2fa

🧑‍💻 Author

Lahari Sri
B.Tech CSE — PKI-2FA Microservice Implementation
