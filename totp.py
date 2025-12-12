# totp.py
# Step 6: TOTP Generation + Verification

import base64
import binascii
from typing import Optional
import pyotp


def _hex_to_base32(hex_seed: str) -> str:
    """
    Convert 64-character hex seed → bytes → base32 string (RFC 3548)
    """
    try:
        seed_bytes = binascii.unhexlify(hex_seed)
    except Exception:
        raise ValueError("Invalid hex seed format")

    # Base32 encode and decode to string
    return base64.b32encode(seed_bytes).decode("utf-8")


def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current 6-digit TOTP code from 64-character hex seed.

    Algorithm: SHA-1 (default for TOTP)
    Period: 30 seconds
    Digits: 6
    """

    # 1. Convert hex seed → base32
    base32_seed = _hex_to_base32(hex_seed)

    # 2. Create TOTP object
    totp = pyotp.TOTP(s=base32_seed, digits=6, interval=30)

    # 3. Generate current TOTP
    code = totp.now()

    # 4. Return 6-digit code
    return code


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify a 6-digit TOTP code with ± valid_window periods allowed.

    Default valid_window = 1 → accepts:
    - previous 30s period
    - current period
    - next 30s period
    """

    # 1. Convert hex seed to base32
    base32_seed = _hex_to_base32(hex_seed)

    # 2. Create TOTP object
    totp = pyotp.TOTP(s=base32_seed, digits=6, interval=30)

    # 3. Verify with time window tolerance
    return totp.verify(code, valid_window=valid_window)
