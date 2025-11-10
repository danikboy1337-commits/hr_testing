#!/usr/bin/env python3
"""
Start FastAPI server with MOCK LDAP authentication for testing
This allows testing the login flow without a real LDAP server
"""
import sys

# Mock the LDAP authentication BEFORE importing anything else
def mock_check_ldap_password(username: str, password: str) -> bool:
    """
    Mock LDAP authentication for testing
    Accepts any whitelisted employee_id with password "test123"
    """
    print(f"🧪 MOCK LDAP: Authenticating {username}")

    if password == "test123":
        print(f"✅ MOCK LDAP: Authentication successful for {username}")
        return True
    else:
        print(f"❌ MOCK LDAP: Authentication failed for {username}")
        return False

# Monkey-patch before importing ldap module
import ldap
original_check = ldap.check_ldap_password
ldap.check_ldap_password = mock_check_ldap_password

print("=" * 70)
print("🧪 MOCK LDAP MODE ACTIVATED")
print("=" * 70)
print()
print("LDAP authentication has been mocked for testing.")
print("Use these test credentials:")
print()
print("  Employee ID: PLACEHOLDER_EMPLOYEE_ID_1")
print("  Password: test123")
print()
print("  Employee ID: PLACEHOLDER_EMPLOYEE_ID_2")
print("  Password: test123")
print()
print("  Employee ID: PLACEHOLDER_EMPLOYEE_ID_3")
print("  Password: test123")
print()
print("=" * 70)
print()

# Now start the FastAPI server
import uvicorn
from main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
