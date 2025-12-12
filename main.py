# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from decrypt_seed import decrypt_seed
from totp import generate_totp_code, verify_totp_code
import time

app = FastAPI()

DATA_PATH = Path("/data/seed.txt")


# ---------------------------
# Request Models
# ---------------------------

class DecryptRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str


# ---------------------------------------------------
# Endpoint 1: POST /decrypt-seed
# ---------------------------------------------------
@app.post("/decrypt-seed")
def api_decrypt_seed(req: DecryptRequest):
    try:
        # 1. Load private key
        with open("student_private.pem", "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)

        # 2. Decrypt using your function
        seed = decrypt_seed(req.encrypted_seed, private_key)

        # 3. Save to /data/seed.txt
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        DATA_PATH.write_text(seed, encoding="utf-8")

        return {"status": "ok"}

    except Exception:
        raise HTTPException(status_code=500, detail="Decryption failed")


# ---------------------------------------------------
# Endpoint 2: GET /generate-2fa
# ---------------------------------------------------
@app.get("/generate-2fa")
def api_generate_2fa():
    try:
        # 1. Check if /data/seed.txt exists
        if not DATA_PATH.exists():
            raise HTTPException(status_code=500, detail="Seed not decrypted yet")

        # 2. Read seed
        hex_seed = DATA_PATH.read_text().strip()

        # 3. Generate TOTP using your function
        code = generate_totp_code(hex_seed)

        # 4. Calculate remaining seconds in current 30s period
        valid_for = 30 - (int(time.time()) % 30)

        return {"code": code, "valid_for": valid_for}

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")


# ---------------------------------------------------
# Endpoint 3: POST /verify-2fa
# ---------------------------------------------------
@app.post("/verify-2fa")
def api_verify_2fa(req: VerifyRequest):
    try:
        # Validate input
        if not req.code:
            raise HTTPException(status_code=400, detail="Missing code")

        # Check seed file exists
        if not DATA_PATH.exists():
            raise HTTPException(status_code=500, detail="Seed not decrypted yet")

        # Load seed
        hex_seed = DATA_PATH.read_text().strip()

        # Verify code (±1 time window)
        is_valid = verify_totp_code(hex_seed, req.code, valid_window=1)

        return {"valid": is_valid}

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
