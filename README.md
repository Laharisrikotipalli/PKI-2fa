# PKI-TOTP (Flask)

## Run locally
1. Activate venv:
   Windows (Git Bash): `source .venv/Scripts/activate`
2. Install deps:
   `python -m pip install -r requirements.txt`
3. Ensure `student_private.pem` and `encrypted_seed.txt` exist in project root.
4. Run:
   `./.venv/Scripts/python -m app.server`
5. Test:
   `curl http://127.0.0.1:8080/totp`
