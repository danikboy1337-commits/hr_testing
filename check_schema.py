#!/usr/bin/env python3
"""
Check HR Schema Tables
Diagnostic script to verify which tables exist in the hr schema
"""

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def check_schema():
    """Check what tables exist in the hr schema"""

    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ DATABASE_URL not found in .env file")
        return

    print(f"\n📊 Connecting to database...")
    # Hide password in output
    safe_url = database_url.split('@')[0].split('://')[0] + "://***:***@" + database_url.split('@')[1]
    print(f"   Database URL: {safe_url}")

    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        print("✅ Connected successfully!\n")

        # Check what schemas exist
        print("=" * 80)
        print("SCHEMAS IN DATABASE:")
        print("=" * 80)
        cur.execute("""
            SELECT schema_name
            FROM information_schema.schemata
            ORDER BY schema_name
        """)
        schemas = cur.fetchall()
        for schema in schemas:
            print(f"  📁 {schema[0]}")

        # Check tables in hr schema
        print("\n" + "=" * 80)
        print("TABLES IN 'hr' SCHEMA:")
        print("=" * 80)
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'hr'
            ORDER BY table_name
        """)
        tables = cur.fetchall()

        if not tables:
            print("  ⚠️  No tables found in 'hr' schema")
        else:
            for table in tables:
                table_name = table[0]

                # Get row count for each table
                try:
                    cur.execute(f"SELECT COUNT(*) FROM hr.{table_name}")
                    count = cur.fetchone()[0]
                    print(f"  ✅ hr.{table_name:<40} ({count} rows)")
                except Exception as e:
                    print(f"  ❌ hr.{table_name:<40} (Error: {e})")

        # Check specific tables needed by the HR Results query
        print("\n" + "=" * 80)
        print("CHECKING REQUIRED TABLES FOR HR RESULTS:")
        print("=" * 80)

        required_tables = [
            'users',
            'departments',
            'user_specialization_tests',
            'specializations',
            'profiles',
            'competencies',
            'competency_self_assessments'
        ]

        missing_tables = []
        for table in required_tables:
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'hr'
                    AND table_name = %s
                )
            """, (table,))
            exists = cur.fetchone()[0]

            if exists:
                cur.execute(f"SELECT COUNT(*) FROM hr.{table}")
                count = cur.fetchone()[0]
                status = "✅" if count > 0 else "⚠️ "
                print(f"  {status} hr.{table:<40} ({count} rows)")
            else:
                print(f"  ❌ hr.{table:<40} (DOES NOT EXIST)")
                missing_tables.append(table)

        # Check columns in users table
        print("\n" + "=" * 80)
        print("COLUMNS IN 'hr.users' TABLE:")
        print("=" * 80)
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'hr' AND table_name = 'users'
            ORDER BY ordinal_position
        """)
        columns = cur.fetchall()

        if columns:
            for col in columns:
                nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
                print(f"  • {col[0]:<30} {col[1]:<20} {nullable}")
        else:
            print("  ⚠️  Table not found or no columns")

        cur.close()
        conn.close()

        print("\n" + "=" * 80)
        print("DIAGNOSIS:")
        print("=" * 80)

        if missing_tables:
            print(f"\n❌ PROBLEM FOUND: {len(missing_tables)} required tables are missing:")
            for table in missing_tables:
                print(f"     • hr.{table}")
            print(f"\n💡 SOLUTION: These are testing-related tables that need to be created.")
            print(f"   The HR Results page is trying to show test results, but there are")
            print(f"   no test results yet because the testing system hasn't been set up.")
            print(f"\n   You have two options:")
            print(f"   1. Create these tables by running the full database schema setup")
            print(f"   2. Modify the HR Results page to show employees even without test data")
        else:
            print("\n✅ All required tables exist!")
            print("   The 500 error might be caused by a different issue.")

        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"\nFull error details:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_schema()
