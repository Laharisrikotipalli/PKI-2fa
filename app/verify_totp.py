import pyotp, base64, binascii

def _to_base32(seed):
    if isinstance(seed, bytes):
        return base64.b32encode(seed).decode().strip("=")
    s = str(seed).strip()
    hex_chars = set("0123456789abcdefABCDEF")
    if len(s) % 2 == 0 and all(c in hex_chars for c in s):
        try:
            b = binascii.unhexlify(s)
            return base64.b32encode(b).decode().strip("=")
        except Exception:
            pass
    return s.upper().strip("=")

def verify_totp(seed, code, window=1, digits=6, interval=30) -> bool:
    b32 = _to_base32(seed)
    totp = pyotp.TOTP(b32, digits=digits, interval=interval)
    return bool(totp.verify(code, valid_window=window))
