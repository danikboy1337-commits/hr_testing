# 📊 Working with Existing Database Structure

**Your Setup:** Database `cds_hb_main` with schema `hr`

This guide explains how to connect the HR Testing Platform to your existing database where all tables are under the `hr` schema.

---

## 🗄️ Your Database Structure

**Database Name:** `cds_hb_main`
**Schema Name:** `hr`
**Table Access:** `SELECT * FROM hr.users`, `SELECT * FROM hr.departments`, etc.

The application has been configured to automatically use the `hr` schema, so you don't need to modify any SQL queries.

---

## ⚙️ How It Works

### Automatic Schema Resolution

The application sets the PostgreSQL `search_path` to `hr,public` when connecting:

```python
# In db/database.py
kwargs={
    "autocommit": True,
    "options": "-c search_path=hr,public"
}
```

This means:
- ✅ When code says `SELECT * FROM users`, PostgreSQL looks in `hr.users`
- ✅ All existing queries work without modification
- ✅ You can still access `public` schema tables if needed

---

## 🔧 Configuration

### Step 1: Update DATABASE_URL

In your `.env` file:

```bash
# OLD format (if database was named hr_testing):
# DATABASE_URL=postgresql://user:password@host:5432/hr_testing

# NEW format (for your existing database):
DATABASE_URL=postgresql://hrapp:YourPassword@YOUR_DB_IP:5432/cds_hb_main
```

**Important:** The database name is `cds_hb_main`, NOT `hr_testing`!

### Step 2: Verify Schema Exists

Connect to your PostgreSQL server and verify:

```bash
psql -h YOUR_DB_IP -U hrapp -d cds_hb_main

# Check if hr schema exists
\dn

# Should show:
#   List of schemas
#   Name  |  Owner
#  -------+--------
#   hr    | ...
#   public | ...
```

### Step 3: Grant Permissions

Make sure your database user has access to the `hr` schema:

```sql
-- Connect as superuser or database owner
sudo -u postgres psql -d cds_hb_main

-- Grant schema usage
GRANT USAGE ON SCHEMA hr TO hrapp;

-- Grant permissions on all tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA hr TO hrapp;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA hr TO hrapp;

-- Grant permissions on future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA hr GRANT ALL ON TABLES TO hrapp;
ALTER DEFAULT PRIVILEGES IN SCHEMA hr GRANT ALL ON SEQUENCES TO hrapp;
```

---

## 📋 Database Initialization

### If Tables Already Exist

If your colleague already created all the tables in `hr` schema:

**Option A: Use Existing Tables** ✅
```bash
# Skip database initialization
# Just configure DATABASE_URL and start the application
```

**Option B: Load Only Data**
```bash
cd /home/ocds_mukhtar/00061221/hr_testing
source venv/bin/activate

# Only load questions and specializations (if tables are empty)
python db/load_questions.py
python db/import_specializations.py
```

### If Tables Don't Exist Yet

If tables need to be created in the `hr` schema:

```bash
# First, ensure hr schema exists
psql -h YOUR_DB_IP -U hrapp -d cds_hb_main -c "CREATE SCHEMA IF NOT EXISTS hr;"

# Then run initialization scripts
cd /home/ocds_mukhtar/00061221/hr_testing
source venv/bin/activate

python db/create_tables.py
python db/run_migration.py db/migration_add_roles_departments.sql
python db/run_migration.py db/migrations/add_test_time_limit.sql
python db/run_migration.py db/migrations/update_manager_evaluations_competency_based.sql
python db/load_questions.py
python db/import_specializations.py
```

**Note:** The scripts will automatically create tables in the `hr` schema because of the search_path configuration.

---

## 🧪 Testing Database Connection

### Test 1: Basic Connection

```bash
psql -h YOUR_DB_IP -U hrapp -d cds_hb_main

# Test schema access
SET search_path TO hr, public;
SELECT COUNT(*) FROM users;
\q
```

### Test 2: Python Connection

Create a test script:

```bash
cd /home/ocds_mukhtar/00061221/hr_testing
nano test_db_connection.py
```

```python
#!/usr/bin/env python3
import asyncio
import sys
sys.path.append('.')

from db.database import init_db_pool, close_db_pool, get_db_connection

async def test_connection():
    print("Testing database connection...")

    try:
        await init_db_pool()
        print("✅ Connection pool initialized")

        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                # Test 1: Check current schema
                await cur.execute("SHOW search_path")
                search_path = await cur.fetchone()
                print(f"✅ Search path: {search_path[0]}")

                # Test 2: Query a table
                await cur.execute("SELECT COUNT(*) FROM users")
                count = await cur.fetchone()
                print(f"✅ Users table: {count[0]} rows")

                # Test 3: Check all tables in hr schema
                await cur.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'hr'
                    ORDER BY table_name
                """)
                tables = await cur.fetchall()
                print(f"✅ Tables in hr schema: {len(tables)}")
                for table in tables:
                    print(f"   - {table[0]}")

        await close_db_pool()
        print("\n✅ All tests passed!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connection())
```

Run the test:

```bash
source venv/bin/activate
python test_db_connection.py
```

---

## 📊 Expected Table Structure

The `hr` schema should contain these tables:

| Table Name | Purpose |
|------------|---------|
| `hr.users` | User accounts |
| `hr.departments` | Organizational departments |
| `hr.profiles` | Job profiles |
| `hr.specializations` | Job specializations |
| `hr.competencies` | Skill competencies |
| `hr.topics` | Test topics |
| `hr.questions` | Test questions (~3000) |
| `hr.user_specialization_selections` | User's chosen specializations |
| `hr.user_specialization_tests` | Active/completed tests |
| `hr.user_test_topics` | Selected topics per test |
| `hr.test_answers` | User answers |
| `hr.ai_recommendations` | AI recommendations |
| `hr.manager_competency_ratings` | Manager ratings |
| `hr.employee_ratings` | (Deprecated) |

---

## 🔍 Troubleshooting

### Error: "relation 'users' does not exist"

**Cause:** Schema not in search path

**Fix 1:** Check DATABASE_URL points to correct database:
```bash
grep DATABASE_URL .env
# Should show: postgresql://...@.../cds_hb_main
```

**Fix 2:** Verify schema exists:
```sql
psql -h YOUR_DB_IP -U hrapp -d cds_hb_main -c "\dn"
```

**Fix 3:** Check application logs:
```bash
# Should see: "✅ Database pool initialized (schema: hr)"
```

### Error: "permission denied for schema hr"

**Cause:** User doesn't have access to hr schema

**Fix:**
```sql
sudo -u postgres psql -d cds_hb_main
GRANT USAGE ON SCHEMA hr TO hrapp;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA hr TO hrapp;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA hr TO hrapp;
```

### Error: "database cds_hb_main does not exist"

**Cause:** Wrong database name in DATABASE_URL

**Fix:** Verify database name with your colleague and update `.env`

---

## 📝 Summary Checklist

- [ ] Database name is `cds_hb_main` (not `hr_testing`)
- [ ] Schema name is `hr`
- [ ] Updated `DATABASE_URL` in `.env` to use `cds_hb_main`
- [ ] Verified `hr` schema exists in database
- [ ] Granted permissions to `hrapp` user on `hr` schema
- [ ] Application logs show "Database pool initialized (schema: hr)"
- [ ] Test connection successful
- [ ] Can query tables: `SELECT * FROM users` works

---

## 💡 Key Points

1. **No Code Changes Needed** - The search_path configuration handles everything automatically

2. **DATABASE_URL Must Use `cds_hb_main`** - This is the most important change

3. **Schema is Set Automatically** - `search_path=hr,public` means tables are accessed from `hr` schema

4. **Permissions Required** - User needs USAGE on schema and ALL on tables/sequences

5. **Backward Compatible** - If you ever need to access `public` schema tables, they're still available

---

**Your Configuration:**
```bash
# In .env
DATABASE_URL=postgresql://hrapp:YOUR_PASSWORD@YOUR_DB_IP:5432/cds_hb_main

# Automatic behavior:
# - All queries use hr schema
# - SELECT * FROM users → SELECT * FROM hr.users
# - No code modifications needed
```

---

**Last Updated:** 2025-01-11
**Database:** `cds_hb_main`
**Schema:** `hr`
