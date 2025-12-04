#!/usr/bin/env python3
"""
Cron script to log 2FA codes every minute.

This version prints the exact required format:

YYYY-MM-DDTHH:MM:SSZ - code: 123456

Behavior:
- Reads a seed from /data/seed.txt by default (or from SEED_FILE env var).
- Accepts the seed in either hex or base32. Whitespace/newlines are ignored.
- Produces a 6-digit TOTP using HMAC-SHA1 and 30s timestep (RFC6238 style).
- Writes the formatted line to stdout (so cron can redirect it to /cron/last_code.txt).
"""

from __future__ import annotations
import os
import sys
import time
import hmac
import hashlib
import struct
from datetime import datetime, timezone
from pathlib import Path
import base64
import re

DEFAULT_SEED_PATH = Path("/data/seed.txt")  # inside container; override with SEED_FILE env var
TIME_STEP = 30
DIGITS = 6


def read_seed(path: Path) -> bytes:
    """Read seed string and return raw bytes. Accept hex or base32."""
    if not path.exists():
        raise FileNotFoundError(f"seed file not found: {path}")
    s = path.read_text().strip()
    if not s:
        raise ValueError("seed file is empty")

    # Remove spaces/newlines
    s_clean = re.sub(r"\s+", "", s)

    # If it looks like hex (even length, hex chars), parse as hex
    if re.fullmatch(r"(?:[0-9a-fA-F]{2})+", s_clean):
        return bytes.fromhex(s_clean)

    # Otherwise, try base32 (add padding if necessary)
    try:
        padding = '=' * (-len(s_clean) % 8)
        return base64.b32decode(s_clean.upper() + padding)
    except Exception as ex:
        raise ValueError(f"seed is neither valid hex nor base32: {ex}")


def generate_totp(seed: bytes, for_time: int | None = None, digits: int = DIGITS, timestep: int = TIME_STEP) -> str:
    """Generate HMAC-SHA1 TOTP code (returns zero-padded string)."""
    if for_time is None:
        for_time = int(time.time())
    counter = int(for_time // timestep)
    # 8-byte big-endian counter
    counter_bytes = struct.pack(">Q", counter)
    hmac_digest = hmac.new(seed, counter_bytes, hashlib.sha1).digest()
    # dynamic truncation
    offset = hmac_digest[-1] & 0x0F
    code_int = struct.unpack(">I", hmac_digest[offset:offset+4])[0] & 0x7FFFFFFF
    code = str(code_int % (10 ** digits)).zfill(digits)
    return code


def main():
    seed_file = Path(os.environ.get("SEED_FILE", DEFAULT_SEED_PATH))
    try:
        seed = read_seed(seed_file)
    except Exception as e:
        # Write a clear error to stderr and exit non-zero so cron logs capture the problem.
        print(f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} - error: {e}", file=sys.stderr)
        sys.exit(1)

    code = generate_totp(seed)
    # EXACT required output format:
    print(f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} - code: {code}")


if __name__ == "__main__":
    main()
