#!/usr/bin/env python3
"""
Diagnostic script to test HR results endpoint
"""
import sys
import os
sys.path.append('.')
os.environ['OPENSSL_CONF'] = os.path.join(os.path.dirname(__file__), 'openssl_legacy.cnf')

import asyncio
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("=" * 70)
print("🔍 TESTING HR RESULTS ENDPOINT")
print("=" * 70)

try:
    print("\n1️⃣ Testing /api/hr/results endpoint...")
    response = client.get("/api/hr/results")

    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCCESS!")
        print(f"Results count: {data.get('count', 0)}")
        if data.get('results'):
            print(f"\nFirst result sample:")
            first = data['results'][0]
            for key, value in first.items():
                print(f"  {key}: {value}")
        else:
            print("\n⚠️ No results found in database")
            print("This is normal if no tests have been completed yet")
    else:
        print(f"\n❌ ERROR!")
        print(f"Response body: {response.text}")

except Exception as e:
    print(f"\n❌ Exception occurred: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Diagnostic complete")
print("=" * 70)
