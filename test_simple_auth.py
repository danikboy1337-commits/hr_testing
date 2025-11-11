#!/usr/bin/env python3
"""
Test SIMPLE authentication directly to verify the fix works
"""

import sys
import os
from dotenv import load_dotenv
import getpass

load_dotenv()

print("=" * 70)
print("🔍 TESTING SIMPLE AUTHENTICATION (NO MD4)")
print("=" * 70)

# Import the fixed ldap module
try:
    from ldap import check_ldap_password
    print("✅ Successfully imported ldap module")
except Exception as e:
    print(f"❌ Failed to import ldap module: {e}")
    sys.exit(1)

# Check if LDAP is enabled
ldap_enabled = os.getenv("LDAP_ENABLED", "False").lower() == "true"
print(f"\nLDAP_ENABLED: {ldap_enabled}")

if not ldap_enabled:
    print("\n⚠️  LDAP is disabled. Set LDAP_ENABLED=True in .env to test real LDAP.")
    print("Testing with mock authentication (password: test123)")

    employee_id = input("\nEmployee ID: ").strip()
    password = getpass.getpass("Password: ")

    result = check_ldap_password(employee_id, password)

    if result:
        print("\n✅ SUCCESS: Mock authentication passed")
    else:
        print("\n❌ FAILED: Use password 'test123' for mock mode")
    sys.exit(0)

# Test real LDAP
print("\n" + "=" * 70)
print("Testing Real LDAP Authentication")
print("=" * 70)

employee_id = input("\nEmployee ID: ").strip()
password = getpass.getpass("Password: ")

print(f"\n🔐 Testing authentication for: {employee_id}")
print("Please wait...\n")

try:
    result = check_ldap_password(employee_id, password)

    if result:
        print("\n✅ SUCCESS: Authentication successful!")
        print("No MD4 errors - SIMPLE authentication is working!")
    else:
        print("\n❌ FAILED: Authentication failed")
        print("Check login_history.log for details")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nIf you see 'unsupported hash type MD4', the ldap3 library may need a workaround.")

print("\n" + "=" * 70)
print("Check login_history.log for detailed authentication logs")
print("=" * 70)
