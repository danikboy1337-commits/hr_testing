#!/usr/bin/env python3
"""
Diagnostic: Check which schema contains the tables
"""

import asyncio
from db.database import init_db_pool, get_db_connection

async def check_table_locations():
    """Check which schema (public vs hr) contains the tables"""

    print("\n" + "=" * 80)
    print("CHECKING TABLE LOCATIONS IN DATABASE")
    print("=" * 80 + "\n")

    await init_db_pool()

    required_tables = [
        'users', 'departments', 'profiles', 'specializations',
        'competencies', 'topics', 'questions',
        'user_specialization_tests', 'user_test_topics',
        'test_answers', 'ai_recommendations'
    ]

    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                for table in required_tables:
                    # Check in public schema
                    await cur.execute("""
                        SELECT COUNT(*)
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = %s
                    """, (table,))
                    in_public = (await cur.fetchone())[0] > 0

                    # Check in hr schema
                    await cur.execute("""
                        SELECT COUNT(*)
                        FROM information_schema.tables
                        WHERE table_schema = 'hr'
                        AND table_name = %s
                    """, (table,))
                    in_hr = (await cur.fetchone())[0] > 0

                    # Get row count if exists
                    row_count = 0
                    if in_public:
                        try:
                            await cur.execute(f"SELECT COUNT(*) FROM public.{table}")
                            row_count = (await cur.fetchone())[0]
                        except:
                            pass
                    elif in_hr:
                        try:
                            await cur.execute(f"SELECT COUNT(*) FROM hr.{table}")
                            row_count = (await cur.fetchone())[0]
                        except:
                            pass

                    # Display result
                    if in_public and in_hr:
                        print(f"⚠️  {table:<30} EXISTS IN BOTH (public + hr) - {row_count} rows")
                    elif in_public:
                        print(f"❌ {table:<30} ONLY in 'public' schema - {row_count} rows")
                    elif in_hr:
                        print(f"✅ {table:<30} ONLY in 'hr' schema - {row_count} rows")
                    else:
                        print(f"❌ {table:<30} DOES NOT EXIST")

                print("\n" + "=" * 80)
                print("DIAGNOSIS:")
                print("=" * 80)

                # Check if all tables are in hr schema
                await cur.execute("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'hr'
                    AND table_name IN %s
                """, (tuple(required_tables),))
                tables_in_hr = (await cur.fetchone())[0]

                # Check if all tables are in public schema
                await cur.execute("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name IN %s
                """, (tuple(required_tables),))
                tables_in_public = (await cur.fetchone())[0]

                if tables_in_hr == len(required_tables):
                    print("\n✅ All tables are in 'hr' schema - migrations should work!")
                elif tables_in_public > 0:
                    print(f"\n❌ PROBLEM: {tables_in_public} tables found in 'public' schema")
                    print("   Tables need to be moved to 'hr' schema OR migrations need to run on public schema")
                    print("\n   SOLUTIONS:")
                    print("   1. Move tables from 'public' to 'hr' schema")
                    print("   2. OR update application to use 'public' schema instead of 'hr'")
                else:
                    print("\n❌ PROBLEM: Base tables don't exist in any schema")
                    print("   You need to run db/init_db.sql first to create base tables")

                print("=" * 80 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_table_locations())
