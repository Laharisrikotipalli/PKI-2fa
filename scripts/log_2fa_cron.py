#!/usr/bin/env python3
import datetime
from pathlib import Path
from generate_totp import generate_totp

BASE = Path(__file__).resolve().parent.parent
SEED = BASE / "keys" / "seed.txt"
LOG_FILE = BASE / "cron" / "last_code.txt"

if SEED.exists():
    seed = SEED.read_text().strip()
    code = generate_totp(seed)
    now = datetime.datetime.utcnow().isoformat() + "Z"
    LOG_FILE.write_text(f"{now}  {code}\n")
