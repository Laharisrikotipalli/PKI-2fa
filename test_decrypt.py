from cryptography.hazmat.primitives import serialization
from decrypt_seed import decrypt_seed

# Load your private key
with open("student_private.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

# Read encrypted seed (base64 string)
with open("encrypted_seed.txt", "r") as f:
    encrypted_seed_b64 = f.read().strip()

# Decrypt using your function
seed = decrypt_seed(encrypted_seed_b64, private_key)

print("Decrypted Seed:", seed)
