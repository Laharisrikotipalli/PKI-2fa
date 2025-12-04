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

# ---------------------------
#         TOTP ENDPOINT
# ---------------------------
@app.route("/totp", methods=["GET"])
def totp_route():
    """
    Returns the current TOTP as JSON: {"totp": "123456"}.
    Order:
      1) Read plaintext seed from SEED_FILE (/app/data/seed.txt)
      2) Read /app/seed.txt
      3) Read /app/encrypted_seed.txt and decrypt using /app/keys/student_private.pem
    """
    # helper paths
    alt_plain = "/app/seed.txt"
    enc_path = "/app/encrypted_seed.txt"
    priv_key_path = "/app/keys/student_private.pem"

    # 1) try SEED_FILE
    seed = None
    try:
        if os.path.isfile(SEED_FILE):
            with open(SEED_FILE, "r") as f:
                s = f.read().strip()
                if s:
                    seed = s
    except Exception as e:
        app.logger.debug("Could not read SEED_FILE: %s", e)

    # 2) try alt plaintext
    if not seed:
        try:
            if os.path.isfile(alt_plain):
                with open(alt_plain, "r") as f:
                    s = f.read().strip()
                    if s:
                        seed = s
        except Exception as e:
            app.logger.debug("Could not read alt_plain seed: %s", e)

    # 3) try encrypted seed + decrypt
    if not seed:
        try:
            if os.path.isfile(enc_path) and os.path.isfile(priv_key_path):
                with open(enc_path, "r") as f:
                    enc = f.read().strip()
                with open(priv_key_path, "rb") as f:
                    priv_bytes = f.read()
                # decrypt_seed imported above takes (encrypted_b64, private_key_bytes)
                plaintext = decrypt_seed(enc, priv_bytes)
                if plaintext:
                    seed = plaintext.strip()
                    # optionally persist decrypted seed for future calls
                    try:
                        os.makedirs(os.path.dirname(SEED_FILE), exist_ok=True)
                        with open(SEED_FILE, "w") as f:
                            f.write(seed)
                    except Exception as e:
                        app.logger.debug("Failed to persist decrypted seed: %s", e)
        except Exception as e:
            app.logger.exception("Failed to decrypt encrypted_seed.txt: %s", e)
            return jsonify({"error": "failed to decrypt encrypted_seed", "detail": str(e)}), 500

    if not seed:
        return jsonify({"error": "seed not found; cannot generate TOTP"}), 500

    # generate totp using your existing generator
    try:
        code = generate_totp(seed)
        return jsonify({"totp": code}), 200
    except Exception as e:
        app.logger.exception("Failed to generate TOTP: %s", e)
        return jsonify({"error": "failed to generate totp", "detail": str(e)}), 500
if __name__ == "__main__":
    # bind to 0.0.0.0 so the container port maps to host
    app.run(host="0.0.0.0", port=8080)
