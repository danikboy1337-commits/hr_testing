#!/usr/bin/env python3
"""
LDAP Connection Diagnostic Tool
Tests LDAP connectivity and authentication
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 70)
print("🔍 LDAP CONNECTION DIAGNOSTIC TOOL")
print("=" * 70)

# Check LDAP configuration
ldap_enabled = os.getenv("LDAP_ENABLED", "False").lower() == "true"
ldap_host = os.getenv("LDAP_HOST", "")
ldap_port = os.getenv("LDAP_PORT", "389")
ldap_domain = os.getenv("LDAP_DOMAIN", "")
ldap_base_dn = os.getenv("LDAP_BASE_DN", "")

print(f"\n📋 Current Configuration:")
print(f"   LDAP_ENABLED: {ldap_enabled}")
print(f"   LDAP_HOST: {ldap_host}")
print(f"   LDAP_PORT: {ldap_port}")
print(f"   LDAP_DOMAIN: {ldap_domain}")
print(f"   LDAP_BASE_DN: {ldap_base_dn}")

if not ldap_enabled:
    print("\n⚠️  WARNING: LDAP_ENABLED=False")
    print("   The application is in MOCK MODE")
    print("   Use password 'test123' for any permitted user")
    print("\n   To enable LDAP, set LDAP_ENABLED=True in .env file")
    sys.exit(0)

print("\n" + "=" * 70)
print("Testing LDAP Connection...")
print("=" * 70)

# Test network connectivity to LDAP server
print(f"\n1️⃣  Testing network connectivity to {ldap_host}:{ldap_port}...")
import socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((ldap_host, int(ldap_port)))
    sock.close()

    if result == 0:
        print(f"   ✅ Port {ldap_port} is open on {ldap_host}")
    else:
        print(f"   ❌ Cannot connect to {ldap_host}:{ldap_port}")
        print(f"   Error code: {result}")
        print("\n   Possible issues:")
        print("   - LDAP_HOST is incorrect (check with IT department)")
        print("   - Firewall blocking connection")
        print("   - LDAP server is down")
        sys.exit(1)
except socket.gaierror:
    print(f"   ❌ Cannot resolve hostname: {ldap_host}")
    print("\n   Possible issues:")
    print("   - LDAP_HOST is incorrect")
    print("   - DNS issue")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Connection error: {e}")
    sys.exit(1)

# Test LDAP authentication
print("\n2️⃣  Testing LDAP authentication module...")
try:
    from ldap import check_ldap_password, PERMITTED_USERS
    print("   ✅ LDAP module loaded successfully")
except ImportError as e:
    print(f"   ❌ Failed to import LDAP module: {e}")
    print("\n   Install ldap3: pip install ldap3")
    sys.exit(1)

# Show permitted users
print("\n3️⃣  Permitted Users:")
if PERMITTED_USERS:
    for emp_id, user_info in PERMITTED_USERS.items():
        print(f"   - {emp_id}: {user_info['name']} ({user_info['role']})")
else:
    print("   ❌ No permitted users configured!")

# Interactive authentication test
print("\n" + "=" * 70)
print("🔐 INTERACTIVE AUTHENTICATION TEST")
print("=" * 70)
print("\nTest authentication with a real employee ID and password")
print("(Password will not be displayed)")

employee_id = input("\nEmployee ID: ").strip()
import getpass
password = getpass.getpass("Password: ")

print(f"\nAttempting to authenticate: {employee_id}")
print("Please wait...")

try:
    result = check_ldap_password(employee_id, password)

    if result:
        print("\n✅ SUCCESS: Authentication successful!")
        print(f"   User {employee_id} can log in to the application")
    else:
        print("\n❌ FAILED: Authentication failed")
        print("\n   Possible issues:")
        print("   - Incorrect password")
        print("   - Employee ID not found in Active Directory")
        print("   - LDAP_DOMAIN is incorrect")
        print("   - User account is disabled in AD")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\n   Check the following:")
    print("   - LDAP server settings (LDAP_HOST, LDAP_PORT, LDAP_DOMAIN)")
    print("   - Network connectivity")
    print("   - Employee ID format")

print("\n" + "=" * 70)
print("Diagnostic complete")
print("=" * 70)
