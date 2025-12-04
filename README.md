## 🚀 Running the Service  
### 👉 Copy all commands below at once

```bash
# 1. Build & Run (Docker Compose)
docker compose up -d --build

# 2. Health Check
curl http://localhost:8080/health

# 3. Generate TOTP
curl http://localhost:8080/generate-2fa

# 4. Verify TOTP
curl -X POST http://localhost:8080/verify-2fa \
  -H "Content-Type: application/json" \
  -d '{"totp":"123456"}'
```
