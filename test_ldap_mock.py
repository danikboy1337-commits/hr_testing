#!/usr/bin/env python3
"""
Mock LDAP Testing - Test authentication without real LDAP server
This allows testing the login flow with placeholder users
"""

import sys
sys.path.append('.')

# Monkey-patch the LDAP authentication to simulate success
def mock_check_ldap_password(username: str, password: str) -> bool:
    """
    Mock LDAP authentication - always returns True for testing
    In production, this would verify against Active Directory
    """
    print(f"🧪 MOCK: Authenticating {username} with password {'*' * len(password)}")

    # Simulate authentication logic
    if password == "test123":  # Accept any user with password "test123"
        print(f"✅ MOCK: Authentication successful for {username}")
        return True
    else:
        print(f"❌ MOCK: Authentication failed for {username}")
        return False

# Replace real LDAP function with mock
import ldap
original_check = ldap.check_ldap_password
ldap.check_ldap_password = mock_check_ldap_password

print("=" * 70)
print("🧪 MOCK LDAP TESTING MODE")
print("=" * 70)
print()
print("LDAP authentication has been mocked for testing.")
print("Any employee_id in the whitelist with password 'test123' will work.")
print()
print("Whitelist (from ldap.py):")
print("  - PLACEHOLDER_EMPLOYEE_ID_1 (role: hr)")
print("  - PLACEHOLDER_EMPLOYEE_ID_2 (role: manager)")
print("  - PLACEHOLDER_EMPLOYEE_ID_3 (role: employee)")
print()
print("Test credentials:")
print("  Employee ID: PLACEHOLDER_EMPLOYEE_ID_1")
print("  Password: test123")
print()
print("=" * 70)
print()

# Test authentication
from ldap import authenticate_user

try:
    print("Test 1: Valid credentials")
    user = authenticate_user("PLACEHOLDER_EMPLOYEE_ID_1", "test123")
    print(f"✅ Success: {user}")
    print()
except Exception as e:
    print(f"❌ Failed: {e}")
    print()

try:
    print("Test 2: Invalid password")
    user = authenticate_user("PLACEHOLDER_EMPLOYEE_ID_1", "wrongpassword")
    print(f"✅ Success: {user}")
    print()
except Exception as e:
    print(f"❌ Expected failure: {e}")
    print()

try:
    print("Test 3: User not in whitelist")
    user = authenticate_user("INVALID_EMPLOYEE_ID", "test123")
    print(f"✅ Success: {user}")
    print()
except Exception as e:
    print(f"❌ Expected failure: {e}")
    print()

print("=" * 70)
print("🎯 Mock testing complete!")
print()
print("To use in your application:")
print("1. Import this file before starting FastAPI")
print("2. Or add MOCK_LDAP=True to your .env")
print("=" * 70)

# Restore original function
ldap.check_ldap_password = original_check
