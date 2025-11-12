#!/usr/bin/env python3
"""
Check database schema for users table
"""
import sys
sys.path.append('.')

print("Checking if users table has required columns...")
print("\nPlease run this SQL query in your database:")
print("-" * 70)
print("""
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;
""")
print("-" * 70)

print("\nExpected columns:")
print("  - id")
print("  - name")
print("  - tab_number  ← REQUIRED")
print("  - company")
print("  - role  ← REQUIRED")
print("  - department_id  ← REQUIRED")
print("  - registered_at")

print("\nIf any of these columns are missing, run:")
print("  python run_migration.py")
