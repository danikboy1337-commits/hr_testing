#!/usr/bin/env python3
"""
Apply database migration to add role and department columns
"""

import sys
import asyncio
sys.path.append('.')

from db.database import get_db_connection

async def run_migration():
    """Apply the migration to add roles and departments"""

    print("=" * 70)
    print("🔄 APPLYING DATABASE MIGRATION")
    print("=" * 70)

    migration_sql = """
    -- 1. Create departments table
    CREATE TABLE IF NOT EXISTS departments (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE,
        description TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    );

    -- 2. Add role and department to users table
    ALTER TABLE users
    ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'employee',
    ADD COLUMN IF NOT EXISTS department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL;

    -- 3. Add index for performance
    CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
    CREATE INDEX IF NOT EXISTS idx_users_department ON users(department_id);

    -- 4. Seed default departments
    INSERT INTO departments (name, description) VALUES
        ('Backend Development', 'Backend разработчики'),
        ('Frontend Development', 'Frontend разработчики'),
        ('Mobile Development', 'Mobile разработчики'),
        ('Data Science', 'Data Scientists и аналитики'),
        ('QA', 'Quality Assurance'),
        ('DevOps', 'DevOps инженеры'),
        ('HR', 'Human Resources'),
        ('Management', 'Менеджмент')
    ON CONFLICT (name) DO NOTHING;

    -- 5. Update existing users to have default values (if any exist)
    UPDATE users SET role = 'employee' WHERE role IS NULL;
    UPDATE users SET department_id = 1 WHERE department_id IS NULL;
    """

    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                print("\n📋 Executing migration SQL...")
                await cur.execute(migration_sql)
                await conn.commit()

                print("✅ Migration completed successfully!")

                # Verify the changes
                await cur.execute("""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = 'users'
                    AND column_name IN ('role', 'department_id')
                    ORDER BY column_name
                """)
                columns = await cur.fetchall()

                print("\n✅ Verified columns added to users table:")
                for col in columns:
                    print(f"   - {col[0]}: {col[1]}")

                # Check departments
                await cur.execute("SELECT COUNT(*) FROM departments")
                dept_count = await cur.fetchone()
                print(f"\n✅ Departments table created with {dept_count[0]} default departments")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("\nIf the migration already ran, this is OK - the schema is already updated.")
        return False

    print("\n" + "=" * 70)
    print("✅ DATABASE MIGRATION COMPLETE")
    print("=" * 70)
    print("\nYou can now restart the application:")
    print("  python main.py")
    print("\n")

    return True

if __name__ == "__main__":
    try:
        asyncio.run(run_migration())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
