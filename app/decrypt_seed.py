import base64
from pathlib import Path
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

BASE = Path(__file__).resolve().parent.parent
PRIVATE_KEY_PATH = BASE / "keys" / "student_private.pem"

def decrypt_seed(encrypted_seed_b64: str) -> str:
    if not isinstance(encrypted_seed_b64, str) or not encrypted_seed_b64.strip():
        raise ValueError("encrypted_seed must be a non-empty base64 string")
    ciphertext = base64.b64decode(encrypted_seed_b64)

    if not PRIVATE_KEY_PATH.exists():
        raise ValueError(f"Private key not found at {PRIVATE_KEY_PATH}")

    pem = PRIVATE_KEY_PATH.read_bytes()
    private_key = serialization.load_pem_private_key(pem, password=None)

    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    try:
        return plaintext.decode("utf-8")
    except Exception:
        return plaintext.hex()
