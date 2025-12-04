from flask import Flask, request, jsonify
import os
from .decrypt_seed import decrypt_seed
from .totp_generator import generate_totp
import sys, json
print("DEBUG: got request body:", file=sys.stderr)
##COMMENTED_BY_FIX print(json.dumps(request.get_json()), file=sys.stderr)
sys.stderr.flush()

# Flask app must be initialized BEFORE route decorators
app = Flask(__name__)

# Where the decrypted seed is stored (docker volume)
SEED_FILE = "/app/data/seed.txt"


# ---------------------------
#         HEALTH CHECK
# ---------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "OK"}), 200


# ---------------------------
#     DECRYPT SEED ENDPOINT
# ---------------------------
@app.route("/decrypt-seed", methods=["POST"])
def decrypt_seed_route():
    """
    1. Read incoming encrypted seed (base64)
    2. Decrypt using student's private key (RSA-OAEP-SHA256)
    3. Save plaintext seed to /app/data/seed.txt (Docker volume)
    """
    data = request.get_json()
    encrypted_seed = data.get("encrypted_seed")

    if not encrypted_seed:
        return jsonify({"error": "Missing encrypted_seed"}), 400

    # Load student private key
    with open("/app/keys/student_private.pem", "rb") as f:
        private_key = f.read()

    # Decrypt
    try:
        plaintext_seed = decrypt_seed(encrypted_seed, private_key)
    except Exception as e:
        return jsonify({"error": f"Decryption failed: {str(e)}"}), 400

    # Ensure data folder exists
    os.makedirs("/app/data", exist_ok=True)

    # Write seed to volume
    with open(SEED_FILE, "w") as f:
        f.write(plaintext_seed)

    return jsonify({"status": "ok", "message": "Seed saved"}), 200


# ---------------------------
#   GENERATE TOTP ENDPOINT
# ---------------------------
@app.route("/generate-2fa", methods=["GET"])
def generate_2fa():
    """
    1. Load seed from disk
    2. Generate current TOTP code
    """
    if not os.path.exists(SEED_FILE):
        return jsonify({"error": "Seed not initialized"}), 400

    with open(SEED_FILE, "r") as f:
        seed = f.read().strip()

    code = generate_totp(seed)
    return jsonify({"code": code}), 200


# ---------------------------
#   VERIFY TOTP ENDPOINT
# ---------------------------
@app.route("/verify-2fa", methods=["POST"])
def verify_2fa():
    """
    1. Read code from request
    2. Load seed from disk
    3. Generate expected code and compare
    """
    data = request.get_json()
    provided = data.get("code")

    if not provided:
        return jsonify({"error": "Missing code"}), 400

    if not os.path.exists(SEED_FILE):
        return jsonify({"error": "Seed not initialized"}), 400

    with open(SEED_FILE, "r") as f:
        seed = f.read().strip()

    expected = generate_totp(seed)

    return jsonify({"valid": provided == expected}), 200


# ---------------------------
#     ENTRY POINT
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

