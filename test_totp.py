from totp import generate_totp_code, verify_totp_code

hex_seed = "ac27f03e3b655b05e8cf59b983b4d80c80f0ceca240d097d8a9a4c307f330a95"

code = generate_totp_code(hex_seed)
print("Generated TOTP:", code)

is_valid = verify_totp_code(hex_seed, code)
print("Is Valid:", is_valid)
