import pyotp, base64, binascii

def _to_base32(seed):
    if isinstance(seed, bytes):
        return base64.b32encode(seed).decode().strip("=")
    s = str(seed).strip()
    # if looks like hex:
    hex_chars = set("0123456789abcdefABCDEF")
    if len(s) % 2 == 0 and all(c in hex_chars for c in s):
        try:
            b = binascii.unhexlify(s)
            return base64.b32encode(b).decode().strip("=")
        except Exception:
            pass
    return s.upper().strip("=")

def generate_totp(seed, digits=6, interval=30) -> str:
    b32 = _to_base32(seed)
    totp = pyotp.TOTP(b32, digits=digits, interval=interval)
    return totp.now()
