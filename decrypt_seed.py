
import base64
import re
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# Regex to validate 64-character hex string
HEX64 = re.compile(r"^[0-9a-f]{64}$")

def decrypt_seed(encrypted_seed_b64: str, private_key):
    """
    Decrypt base64-encoded encrypted seed using RSA/OAEP + SHA-256.

    Args:
        encrypted_seed_b64: Base64-encoded ciphertext string
        private_key: Loaded RSA private key object

    Returns:
        64-character lowercase hex seed
    """

    # 1. Base64 decode
    try:
        ciphertext = base64.b64decode(encrypted_seed_b64)
    except Exception:
        raise ValueError("Invalid base64 input for encrypted seed")

    # 2. RSA-OAEP decrypt (SHA-256)
    try:
        plaintext_bytes = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception as e:
        raise ValueError("RSA OAEP decryption failed") from e

    # 3. Convert decrypted bytes → UTF-8 string
    try:
        seed = plaintext_bytes.decode("utf-8").strip().lower()
    except Exception:
        raise ValueError("Decrypted data is not valid UTF-8")

    # 4. Validate 64-char lowercase hex string
    if not HEX64.fullmatch(seed):
        raise ValueError("Decrypted seed must be a 64-character lowercase hex string")

    # 5. Return final seed
    return seed
