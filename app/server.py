from flask import Flask, request, jsonify
import os
from .decrypt_seed import decrypt_seed
from .totp_generator import generate_totp

app = Flask(__name__)

SEED_FILE = "/app/data/seed.txt"

@app.route("/decrypt-seed", methods=["POST"])
def decrypt_seed_route():
    """
    Decrypt encrypted seed using student's private key (RSA OAEP SHA256),
    save plaintext seed to persistent volume.
    """
    data = request.get_json()
    encrypted_seed = data.get("encrypted_seed")

    if not encrypted_seed:
        return jsonify({"error": "Missing encrypted_seed"}), 400

    # Load student's private key
    with open("/app/keys/student_private.pem", "rb") as f:
        private_key = f.read()

    # Decrypt seed
    seed_plaintext = decrypt_seed(encrypted_seed, private_key)

    # Persist it to docker volume
    os.makedirs("/app/data", exist_ok=True)
    with open(SEED_FILE, "w") as f:
        f.write(seed_plaintext)

    return jsonify({"status": "ok", "message": "Seed saved"}), 200


@app.route("/generate-2fa", methods=["GET"])
def generate_2fa():
    """
    Read seed from volume, generate TOTP.
    """
    if not os.path.exists(SEED_FILE):
        return jsonify({"error": "Seed not initialized"}), 400

    with open(SEED_FILE) as f:
        seed = f.read().strip()

    totp_code = generate_totp(seed)
    return jsonify({"code": totp_code})


@app.route("/verify-2fa", methods=["POST"])
def verify_2fa():
    """
    Validate a provided TOTP code using stored seed.
    """
    data = request.get_json()
    provided_code = data.get("code")

    if not provided_code:
        return jsonify({"error": "Missing code"}), 400

    if not os.path.exists(SEED_FILE):
        return jsonify({"error": "Seed not initialized"}), 400

    with open(SEED_FILE) as f:
        seed = f.read().strip()

    expected = generate_totp(seed)

    return jsonify({"valid": provided_code == expected})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
