# Secure PKI & TOTP Authentication Microservice

A high-performance, containerized microservice designed for secure seed exchange and authentication. The system leverages **Public Key Infrastructure (PKI)** for encrypted seed transmission and the **Time-based One-Time Password (TOTP)** algorithm for multi-factor authentication.

---

##  System Architecture
The microservice is built on a decoupled architecture ensuring security at rest and in transit:
1. **Asymmetric Decryption**: Uses RSA-2048 to decrypt incoming authentication seeds.
2. **Seed Normalization**: Implements strict 64-character hex slicing to maintain compatibility with standard TOTP generators.
3. **Automated Background Tasks**: A Linux-based cron service handles high-frequency logging of authentication codes.
4. **Data Persistence**: Docker volume mapping ensures that critical authentication data survives container lifecycles.

---

## Technical Specifications
- **Backend Framework**: FastAPI (Python 3.11)
- **Security Primitives**: RSA (OAEP Padding), SHA-256
- **MFA Protocol**: TOTP (RFC 6238)
- **Infrastructure**: Docker, Docker Compose, Linux Cron

----

##  Repository Structure
- `main.py`: Primary API gateway handling decryption and verification.
- `cron_write_totp.py`: Background automation script for logging 2FA states.
- `instructor_public.pem`: Public certificate used for system-wide commit verification.
- `Dockerfile`: Multi-process container configuration.
- `docker-compose.yml`: Infrastructure-as-Code for persistent storage and networking.

----

## API Reference

### 1. Seed Decryption
`POST /decrypt-seed`
- **Purpose**: Receives an RSA-encrypted seed, decrypts it using the private key, and persists exactly 64 characters to protected storage.
- **Payload**: `{"encrypted_seed": "BASE64_STRING"}`

### 2. TOTP Generation
`GET /generate-2fa`
- **Purpose**: Generates and returns the current 6-digit authentication code in real-time.

### 3. Verification
`POST /verify-2fa`
- **Purpose**: Validates a user-submitted code against the current server-side seed.

---

##  Proof of Implementation
The `/screenshots` directory contains validated evidence of the system's operational state:
- **Seed Validation**: Verification of the 64-character hex seed integrity.
- **Service Logs**: Automated cron logs featuring ISO-8601 timestamps and 2FA code history.
- **API Response**: Successful 6-digit code generation via REST client.
---
##  Getting Started
1. **Clone the repository**:
   ```bash
   git clone (https://github.com/Laharisrikotipalli/pki-2fa.git)
**Launch the Microservice:**

Bash
```
docker compose up --build -d
```
**Verify Background Logs:**

Bash
```
docker exec -it pki-2fa-app-1 cat /data/cron.log
```
---
***Developer:*** Lahari Srikotipalli

***Student ID:*** 23MH1A05I0
