from app.core.security import create_access_token, decode_access_token, hash_password, verify_password

def test_password_hash_round_trip():
    password = "Strong-password-123"
    encoded = hash_password(password)
    assert encoded != password
    assert verify_password(password, encoded)
    assert not verify_password("wrong-password", encoded)

def test_token_round_trip():
    token = create_access_token("user-123", "ADMIN", expires_in=60)
    claims = decode_access_token(token)
    assert claims["sub"] == "user-123"
    assert claims["role"] == "ADMIN"
