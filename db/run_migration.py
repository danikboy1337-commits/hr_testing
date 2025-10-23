import asyncio
import sys
import os

# FIX для Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import init_db_pool, close_db_pool, get_db_connection


async def run_migration():
    """Run the roles and departments migration"""
    print("🚀 Running migration: Add Roles and Departments...")

    await init_db_pool()

    # Read migration SQL
    with open('db/migration_add_roles_departments.sql', 'r', encoding='utf-8') as f:
        sql = f.read()

    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql)

        print("✅ Migration completed successfully!")

        # Verify migration
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                # Check departments
                await cur.execute("SELECT COUNT(*) FROM departments")
                dept_count = (await cur.fetchone())[0]
                print(f"   📁 Departments created: {dept_count}")

                # Check if columns exist
                await cur.execute("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'users' AND column_name IN ('role', 'department_id')
                """)
                cols = await cur.fetchall()
                print(f"   👤 Users table columns added: {[col[0] for col in cols]}")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        await close_db_pool()


if __name__ == "__main__":
    asyncio.run(run_migration())
