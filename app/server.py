from flask import Flask, request, jsonify
from pathlib import Path

# Attempt local imports first (works inside container) then fallback
try:
    from app.decrypt_seed import decrypt_seed
    from app.generate_totp import generate_totp
    from app.verify_totp import verify_totp
except Exception:
    from decrypt_seed import decrypt_seed
    from generate_totp import generate_totp
    from verify_totp import verify_totp

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
KEYS_DIR = BASE_DIR / "keys"
SEED_FILE = KEYS_DIR / "seed.txt"


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "pki-2fa"}), 200


@app.post("/decrypt-seed")
def decrypt_seed_route():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "bad_request", "message": "invalid json"}), 400

    enc = data.get("encrypted_seed") if isinstance(data, dict) else None
    if not enc:
        return jsonify({"error": "missing_parameter", "message": "encrypted_seed required"}), 400

    try:
        plaintext = decrypt_seed(enc)
        KEYS_DIR.mkdir(parents=True, exist_ok=True)
        SEED_FILE.write_text(plaintext.strip(), encoding="utf-8")
        return jsonify({"status": "ok", "message": "Seed decrypted and persisted"}), 200
    except Exception as e:
        return jsonify({"error": "decryption_failed", "message": str(e)}), 500


@app.get("/generate-2fa")
def generate_2fa():
    if not SEED_FILE.exists():
        return jsonify({"error": "seed_missing", "message": f"Seed file not present at {SEED_FILE}"}), 404
    seed = SEED_FILE.read_text(encoding="utf-8").strip()
    try:
        totp = generate_totp(seed)
        return jsonify({"totp": str(totp)}), 200
    except Exception as e:
        return jsonify({"error": "totp_error", "message": str(e)}), 500


@app.post("/verify-2fa")
def verify_2fa():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "bad_request", "message": "invalid json"}), 400

    code = data.get("totp") if isinstance(data, dict) else None
    if not code:
        return jsonify({"error": "missing_parameter", "message": "totp required"}), 400

    if not SEED_FILE.exists():
        return jsonify({"error": "seed_missing", "message": f"Seed file not present at {SEED_FILE}"}), 404

    seed = SEED_FILE.read_text(encoding="utf-8").strip()
    try:
        valid = verify_totp(seed, str(code))
        return jsonify({"valid": bool(valid)}), 200
    except Exception as e:
        return jsonify({"error": "verify_error", "message": str(e)}), 500


if __name__ == "__main__":
    # correct quoting here — use single quotes inside Python
    app.run(host='0.0.0.0', port=8080)
