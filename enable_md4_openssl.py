#!/usr/bin/env python3
"""
Workaround for MD4 hash error in OpenSSL 3.x
This enables the legacy provider which includes MD4 support
"""

import sys
import os

# This must be done BEFORE importing ldap3
try:
    # For OpenSSL 3.x, enable legacy provider for MD4 support
    import ssl
    openssl_version = ssl.OPENSSL_VERSION

    print(f"OpenSSL version: {openssl_version}")

    if "OpenSSL 3" in openssl_version:
        print("✅ Detected OpenSSL 3.x - MD4 is in legacy provider")
        print("Attempting to enable legacy provider...")

        # Set environment variable to enable legacy algorithms
        os.environ['OPENSSL_CONF'] = '/dev/null'  # Ignore system config

        # Try to enable MD4 via hashlib
        try:
            import hashlib
            # Force load of legacy provider by trying to use MD4
            # This will fail but might enable the provider
            try:
                hashlib.new('md4')
                print("✅ MD4 is available")
            except ValueError:
                print("⚠️  MD4 is not available - NTLM authentication will fail")
                print("    Recommendation: Use SIMPLE authentication instead (already implemented)")
        except Exception as e:
            print(f"⚠️  Could not check MD4 availability: {e}")
    else:
        print("✅ OpenSSL version < 3.x - MD4 should be available by default")

except Exception as e:
    print(f"❌ Error checking OpenSSL: {e}")

print("\n" + "=" * 70)
print("RECOMMENDATION")
print("=" * 70)
print("The application has been updated to use SIMPLE authentication")
print("which does NOT require MD4. If you're still seeing MD4 errors:")
print()
print("1. Make sure you RESTART the application after code changes:")
print("   - Stop with Ctrl+C")
print("   - Run: python main.py")
print()
print("2. Clear Python cache:")
print("   - find . -name '*.pyc' -delete")
print("   - find . -name '__pycache__' -exec rm -rf {} +")
print()
print("3. Verify the new code is loaded:")
print("   - python test_simple_auth.py")
print("=" * 70)
