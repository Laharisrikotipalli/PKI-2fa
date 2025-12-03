#!/usr/bin/env python3
"""
Generate commit proof:
 - reads latest git commit hash
 - signs ASCII commit hash with student_private.pem using RSA-PSS-SHA256
 - encrypts signature with instructor_public.pem using RSA-OAEP-SHA256
 - base64-encodes the encrypted signature and prints result
Outputs two lines:
Commit Hash: <40-hex>
Encrypted Signature: <base64 single-line>
"""

import subprocess
import sys
import os
import base64

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend

# --- helpers ---
def get_latest_commit_hash() -> str:
    try:
        out = subprocess.check_output(["git", "log", "-1", "--format=%H"], stderr=subprocess.STDOUT)
        h = out.decode("utf-8").strip()
        if len(h) != 40 or any(c not in "0123456789abcdefABCDEF" for c in h):
            raise ValueError(f"Unexpected commit hash: '{h}'")
        return h
    except subprocess.CalledProcessError as e:
        print("ERROR: git command failed:", e.output.decode("utf-8"), file=sys.stderr)
        raise
    except FileNotFoundError:
        raise RuntimeError("git not found in PATH")

def load_private_key(path: str):
    with open(path, "rb") as f:
        data = f.read()
    return serialization.load_pem_private_key(data, password=None, backend=default_backend())

def load_public_key(path: str):
    with open(path, "rb") as f:
        data = f.read()
    return serialization.load_pem_public_key(data, backend=default_backend())

def sign_message(message: str, private_key) -> bytes:
    """
    Sign ASCII message bytes using RSA-PSS-SHA256 with MGF1(SHA256) and max salt length.
    """
    msg_bytes = message.encode("utf-8")  # CRITICAL: sign ASCII/UTF-8 bytes of hex string
    sig = private_key.sign(
        msg_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return sig

def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    """
    Encrypt data using RSA-OAEP with SHA-256 and MGF1(SHA-256)
    """
    cipher = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return cipher

# --- main ---
def main():
    # file paths
    priv_path = "student_private.pem"
    instr_pub_path = "instructor_public.pem"

    # quick checks
    for p in (priv_path, instr_pub_path):
        if not os.path.isfile(p):
            print(f"ERROR: required file not found: {p}", file=sys.stderr)
            sys.exit(2)

    # 1. get commit hash
    commit_hash = get_latest_commit_hash()

    # 2. load keys
    try:
        priv = load_private_key(priv_path)
    except Exception as e:
        print(f"ERROR: failed to load private key: {e}", file=sys.stderr)
        sys.exit(3)
    try:
        instr_pub = load_public_key(instr_pub_path)
    except Exception as e:
        print(f"ERROR: failed to load instructor public key: {e}", file=sys.stderr)
        sys.exit(4)

    # 3. sign commit hash (ASCII)
    signature = sign_message(commit_hash, priv)

    # 4. encrypt signature with instructor public key
    encrypted = encrypt_with_public_key(signature, instr_pub)

    # 5. base64 encode
    b64 = base64.b64encode(encrypted).decode("ascii")

    # Output
    print(f"Commit Hash: {commit_hash}")
    print(f"Encrypted Signature: {b64}")

if __name__ == "__main__":
    main()
