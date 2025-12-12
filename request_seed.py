import json
import requests

# Instructor API endpoint
API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

# Your details
STUDENT_ID = "23MH1A05I0"
GITHUB_URL = "https://github.com/Laharisrikotipalli/pki-2fa"

# Read your student public key (PEM format)
with open("student_public.pem", "r") as f:
    public_key = f.read()

# Prepare the request payload
payload = {
    "student_id": STUDENT_ID,
    "github_repo_url": GITHUB_URL,
    "public_key": public_key
}

print("Sending request to instructor API...")
response = requests.post(API_URL, json=payload, timeout=30)

print("Status code:", response.status_code)
print("Response:", response.text)

# Save encrypted seed
if response.status_code == 200:
    data = response.json()
    encrypted = data.get("encrypted_seed")
    if encrypted:
        with open("encrypted_seed.txt", "w") as f:
            f.write(encrypted)
        print("\nEncrypted seed saved to encrypted_seed.txt")
    else:
        print("\nERROR: No 'encrypted_seed' in response.")
else:
    print("\nAPI request failed.")
