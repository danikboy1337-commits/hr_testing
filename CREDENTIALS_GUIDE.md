# 🔐 LDAP and PostgreSQL Configuration Guide

**Your Installation Path:** `/home/ocds_mukhtar/00061221/hr_testing`

This guide explains exactly where and how to configure LDAP and PostgreSQL credentials for your HR Testing Platform.

---

## 📍 Where to Put All Credentials

All credentials go in **ONE FILE**: `.env`

**File Location:**
```
/home/ocds_mukhtar/00061221/hr_testing/.env
```

This file does NOT exist yet - you need to create it from the template.

---

## 🚀 Step-by-Step Configuration

### Step 1: Create the .env File

```bash
cd /home/ocds_mukhtar/00061221/hr_testing

# Copy template to create .env
cp .env.template .env

# Edit with your credentials
nano .env
```

---

### Step 2: Configure PostgreSQL Credentials

**Find this section in `.env`:**

```bash
# ============================================
# DATABASE CONFIGURATION
# ============================================
DATABASE_URL=postgresql://user:password@localhost:5432/hr_testing
```

**Replace with your PostgreSQL server details:**

```bash
DATABASE_URL=postgresql://USERNAME:PASSWORD@SERVER_IP:PORT/DATABASE_NAME
```

**Example (fill in YOUR values):**
```bash
# If your PostgreSQL is on a separate server at 10.20.30.40
DATABASE_URL=postgresql://hrapp:MySecurePassword123@10.20.30.40:5432/hr_testing

# Breakdown:
# postgresql://    - Protocol (always this)
# hrapp            - PostgreSQL username (you'll create this)
# MySecurePassword123 - PostgreSQL password (you'll create this)
# 10.20.30.40      - PostgreSQL server IP address
# 5432             - PostgreSQL port (usually 5432)
# hr_testing       - Database name (you'll create this)
```

**What you need from your PostgreSQL server:**
- ✅ Server IP address or hostname
- ✅ Port number (usually 5432)
- ✅ Username (you'll create a new user called `hrapp`)
- ✅ Password (you'll set this when creating the user)
- ✅ Database name (you'll create a new database called `hr_testing`)

---

### Step 3: Configure LDAP Credentials

**Find this section in `.env`:**

```bash
# ============================================
# LDAP/ACTIVE DIRECTORY AUTHENTICATION
# ============================================
LDAP_ENABLED=False

# LDAP Server Configuration
LDAP_DOMAIN=UNIVERSAL
LDAP_HOST=ldap-server.company.local
LDAP_PORT=389
LDAP_BASE_DN=OU=Employees,DC=company,DC=local
LDAP_USE_SSL=False
LDAP_USE_TLS=False
```

**Replace with your LDAP server details (from IT department):**

```bash
# Enable LDAP authentication
LDAP_ENABLED=True

# LDAP Server Configuration
LDAP_DOMAIN=YOUR_DOMAIN_NAME        # Example: HALYKBANK
LDAP_HOST=YOUR_LDAP_SERVER_IP       # Example: 10.50.60.70 or ad.halykbank.kz
LDAP_PORT=389                        # 389 for LDAP, 636 for LDAPS
LDAP_BASE_DN=YOUR_BASE_DN           # Example: OU=Employees,DC=halykbank,DC=kz
LDAP_USE_SSL=False                   # True if using port 636
LDAP_USE_TLS=True                    # True for STARTTLS (you said you use TLS)
LDAP_TIMEOUT=10
```

**Example (fill in YOUR values from IT department):**
```bash
LDAP_ENABLED=True
LDAP_DOMAIN=HALYKBANK
LDAP_HOST=10.50.60.70
LDAP_PORT=389
LDAP_BASE_DN=OU=Employees,DC=halykbank,DC=kz
LDAP_USE_SSL=False
LDAP_USE_TLS=True
LDAP_TIMEOUT=10
```

**What you need from your IT department:**
- ✅ LDAP server IP address or hostname
- ✅ LDAP port (389 for LDAP, 636 for LDAPS)
- ✅ Domain name (e.g., HALYKBANK, UNIVERSAL, etc.)
- ✅ Base DN (Distinguished Name) - this is like the "root path" in Active Directory
- ✅ Whether to use SSL or TLS
- ✅ A test employee ID and password to verify it works

---

### Step 4: Configure Employee Whitelist

**Find this section in `.env`:**

```bash
# ============================================
# PERMITTED USERS WHITELIST
# ============================================
PERMITTED_USERS=PLACEHOLDER_EMPLOYEE_ID_1:Test User 1:hr:read,write,admin
```

**Replace with real employee data (from HR department):**

**Format:**
```
EMPLOYEE_ID:Full Name:role:permissions;EMPLOYEE_ID:Full Name:role:permissions
```

**Roles:**
- `hr` - HR staff (full access to all features)
- `manager` - Managers (can evaluate employees)
- `employee` - Regular employees (can take tests)

**Permissions:**
- `read` - Can view data
- `write` - Can modify data
- `admin` - Administrative access

**Example (fill in YOUR employees):**
```bash
PERMITTED_USERS=00058215:Nadir Sultanov:hr:read,write,admin;00037099:Saltanat Kenzhebekova:hr:read,write,admin;00012345:Manager Name:manager:read,write;00067890:Employee Name:employee:read
```

**Important Notes:**
- Separate multiple users with semicolon `;`
- Use employee IDs exactly as they appear in Active Directory
- Use colons `:` to separate fields
- Use commas `,` to separate permissions
- **No spaces** around colons or semicolons!

---

### Step 5: Generate JWT Secret Key

**Find this section in `.env`:**

```bash
# ============================================
# JWT SECURITY
# ============================================
JWT_SECRET_KEY=PLACEHOLDER-SECRET-KEY-CHANGE-IN-PRODUCTION-MIN-32-CHARS
```

**Generate a secure secret key:**

```bash
cd /home/ocds_mukhtar/00061221/hr_testing

# If you have Python virtual environment already:
source venv/bin/activate
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use system Python:
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Copy the output and paste it in `.env`:**

```bash
JWT_SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

**This key is used to encrypt user login tokens. Keep it secret!**

---

### Step 6: Verify .env File

Your final `.env` file should look like this (with YOUR values):

```bash
# ============================================
# DATABASE CONFIGURATION
# ============================================
DATABASE_URL=postgresql://hrapp:YourPassword@10.20.30.40:5432/hr_testing

# ============================================
# LDAP/ACTIVE DIRECTORY AUTHENTICATION
# ============================================
LDAP_ENABLED=True
LDAP_DOMAIN=HALYKBANK
LDAP_HOST=10.50.60.70
LDAP_PORT=389
LDAP_BASE_DN=OU=Employees,DC=halykbank,DC=kz
LDAP_USE_SSL=False
LDAP_USE_TLS=True
LDAP_TIMEOUT=10

# ============================================
# PERMITTED USERS WHITELIST
# ============================================
PERMITTED_USERS=00058215:Nadir Sultanov:hr:read,write,admin;00037099:Saltanat:hr:read,write,admin

# ============================================
# JWT SECURITY
# ============================================
JWT_SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6

# ============================================
# APPLICATION SETTINGS
# ============================================
HOST=0.0.0.0
PORT=8000
DEBUG=False

# ============================================
# OPTIONAL SETTINGS (leave empty or comment out)
# ============================================
# ANTHROPIC_API_KEY=  (not needed)
# RECAPTCHA_SITE_KEY=
# RECAPTCHA_SECRET_KEY=
```

**Secure the file:**
```bash
chmod 600 /home/ocds_mukhtar/00061221/hr_testing/.env
```

---

## 🗄️ PostgreSQL Migration/Setup Process

### What "Migration" Means

**Migration = Setting up the database for the first time**

This involves:
1. Creating a new database on your PostgreSQL server
2. Creating a user with access to that database
3. Creating all the tables (users, tests, questions, etc.)
4. Loading initial data (questions, specializations, departments)

### Step-by-Step PostgreSQL Setup

#### 1. Connect to PostgreSQL Server

**On your PostgreSQL server** (or remotely if you have access):

```bash
# If PostgreSQL is on the same machine:
sudo -u postgres psql

# If PostgreSQL is on a different server:
ssh username@POSTGRESQL_SERVER_IP
sudo -u postgres psql
```

#### 2. Create Database and User

```sql
-- Create database
CREATE DATABASE hr_testing;

-- Create user with strong password
CREATE USER hrapp WITH PASSWORD 'YourStrongPasswordHere123!';

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE hr_testing TO hrapp;

-- Connect to the database
\c hr_testing

-- Grant schema privileges
GRANT ALL PRIVILEGES ON SCHEMA public TO hrapp;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO hrapp;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO hrapp;

-- Ensure future tables also have privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO hrapp;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO hrapp;

-- Verify
\l hr_testing

-- Exit
\q
```

#### 3. Test Connection from Application Server

**On your application server** (where the code is):

```bash
# Test connection using psql client
psql -h POSTGRESQL_SERVER_IP -p 5432 -U hrapp -d hr_testing

# Enter password when prompted
# If successful, you'll see:
# hr_testing=>

# Exit
\q
```

**If connection fails:**
- Check `postgresql.conf` - ensure `listen_addresses = '*'` or your app server IP
- Check `pg_hba.conf` - add entry for your app server IP
- Check firewall - ensure port 5432 is open

#### 4. Initialize Database Schema

**On your application server:**

```bash
cd /home/ocds_mukhtar/00061221/hr_testing

# Activate virtual environment (if you haven't created it yet, see below)
source venv/bin/activate

# Create all tables
python db/create_tables.py

# You should see:
# ✅ Successfully created all tables
```

#### 5. Run Migrations

```bash
# Still in virtual environment
source venv/bin/activate

# Run migrations in order
python db/run_migration.py db/migration_add_roles_departments.sql
python db/run_migration.py db/migrations/add_test_time_limit.sql
python db/run_migration.py db/migrations/update_manager_evaluations_competency_based.sql
```

#### 6. Load Initial Data

```bash
# Load test questions (~3000 questions)
python db/load_questions.py

# Load specializations and competencies
python db/import_specializations.py
```

#### 7. Verify Data Loaded

```bash
# Connect to database
psql -h POSTGRESQL_SERVER_IP -p 5432 -U hrapp -d hr_testing

# Check data
SELECT COUNT(*) FROM questions;       -- Should show ~3000
SELECT COUNT(*) FROM specializations; -- Should show 17
SELECT COUNT(*) FROM departments;     -- Should show 8

\q
```

**Done! Your PostgreSQL database is now ready.**

---

## 🔐 LDAP Migration/Setup Process

### What "LDAP Migration" Means

**LDAP Migration = Configuring the application to use your company's Active Directory**

This does NOT involve moving any LDAP data. It just means:
1. Configuring the application to connect to your existing LDAP server
2. Testing that authentication works
3. Setting up the employee whitelist

### Step-by-Step LDAP Setup

#### 1. Get LDAP Details from IT Department

**You need to ask your IT department for:**

| Information | Example | Your Value |
|-------------|---------|------------|
| LDAP Server IP/Hostname | `10.50.60.70` or `ad.halykbank.kz` | _____________ |
| LDAP Port | `389` (LDAP) or `636` (LDAPS) | _____________ |
| Domain Name | `HALYKBANK` | _____________ |
| Base DN | `OU=Employees,DC=halykbank,DC=kz` | _____________ |
| Use TLS? | `Yes` or `No` | _____________ |
| Test Employee ID | `00058215` | _____________ |
| Test Password | `(temporary password)` | _____________ |

#### 2. Configure LDAP in .env

**Edit `.env` file:**

```bash
nano /home/ocds_mukhtar/00061221/hr_testing/.env
```

**Update LDAP section with values from IT:**

```bash
LDAP_ENABLED=True
LDAP_DOMAIN=HALYKBANK              # From IT
LDAP_HOST=10.50.60.70              # From IT
LDAP_PORT=389                      # From IT
LDAP_BASE_DN=OU=Employees,DC=halykbank,DC=kz  # From IT
LDAP_USE_SSL=False
LDAP_USE_TLS=True                  # You mentioned you use TLS
LDAP_TIMEOUT=10
```

#### 3. Get Employee Whitelist from HR

**You need a list of employees who can access the system.**

**Format to request from HR:**

| Employee ID | Full Name | Role | Permissions |
|-------------|-----------|------|-------------|
| 00058215 | Nadir Sultanov | hr | read,write,admin |
| 00037099 | Saltanat Kenzhebekova | hr | read,write,admin |
| 00012345 | Manager Name | manager | read,write |
| 00067890 | Employee Name | employee | read |

**Convert to .env format:**

```bash
PERMITTED_USERS=00058215:Nadir Sultanov:hr:read,write,admin;00037099:Saltanat Kenzhebekova:hr:read,write,admin;00012345:Manager Name:manager:read,write;00067890:Employee Name:employee:read
```

**Add to `.env` file.**

#### 4. Test LDAP Connection

**Before starting the application, test LDAP works:**

```bash
cd /home/ocds_mukhtar/00061221/hr_testing
source venv/bin/activate

# Run test script
python test_ldap_connection.py
```

**You'll be prompted:**
```
Enter test employee ID: 00058215
Enter test password: ********
```

**Expected output if successful:**
```
✅ SUCCESS! LDAP authentication working
LDAP server is reachable and authentication is functional.
```

**If it fails:**
- Check LDAP_HOST is correct (ping it: `ping 10.50.60.70`)
- Check LDAP_PORT is correct
- Check firewall allows connection from your server to LDAP server
- Check LDAP_BASE_DN is correct
- Check LDAP_DOMAIN is correct
- Ask IT department to verify

#### 5. Check Authentication Logs

```bash
# After testing, check the log file
cat /home/ocds_mukhtar/00061221/hr_testing/login_history.log
```

**You should see authentication attempts logged.**

**Done! Your LDAP authentication is now configured.**

---

## 📋 Complete Setup Checklist

### Prerequisites
- [ ] PostgreSQL server accessible from your application server
- [ ] LDAP server details from IT department
- [ ] Employee whitelist from HR department
- [ ] Application code at `/home/ocds_mukhtar/00061221/hr_testing`

### PostgreSQL Setup
- [ ] Connected to PostgreSQL server
- [ ] Created database `hr_testing`
- [ ] Created user `hrapp` with strong password
- [ ] Granted privileges
- [ ] Configured `postgresql.conf` for remote access (if needed)
- [ ] Configured `pg_hba.conf` to allow app server IP
- [ ] Tested connection from app server
- [ ] Added `DATABASE_URL` to `.env` file
- [ ] Created virtual environment: `python3 -m venv venv`
- [ ] Activated venv: `source venv/bin/activate`
- [ ] Installed dependencies: `pip install -r requirements.txt`
- [ ] Ran `db/create_tables.py` successfully
- [ ] Ran all migrations successfully
- [ ] Loaded questions successfully
- [ ] Loaded specializations successfully
- [ ] Verified data in database

### LDAP Setup
- [ ] Obtained LDAP server IP from IT
- [ ] Obtained LDAP domain from IT
- [ ] Obtained LDAP Base DN from IT
- [ ] Confirmed TLS usage with IT
- [ ] Obtained test employee credentials from IT
- [ ] Configured LDAP settings in `.env`
- [ ] Set `LDAP_ENABLED=True`
- [ ] Obtained employee whitelist from HR
- [ ] Formatted whitelist correctly
- [ ] Added whitelist to `.env` as `PERMITTED_USERS`
- [ ] Tested LDAP connection with test script
- [ ] Verified authentication in `login_history.log`

### Security
- [ ] Generated JWT secret key
- [ ] Added JWT secret to `.env`
- [ ] Set `.env` file permissions: `chmod 600 .env`
- [ ] Verified `.env` not in git (already in .gitignore)

### Application
- [ ] All configuration in `.env` complete
- [ ] All dependencies installed
- [ ] Database initialized and data loaded
- [ ] LDAP tested and working
- [ ] Ready to start application

---

## 🚀 Starting the Application (After Configuration)

Once everything above is complete:

```bash
cd /home/ocds_mukhtar/00061221/hr_testing
source venv/bin/activate

# Test run (development mode)
python main.py

# Or production mode with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Access the application:**
```
http://YOUR_SERVER_IP:8000/login
```

---

## 🆘 Troubleshooting

### PostgreSQL Connection Issues

**Error: "connection refused"**
- Check PostgreSQL is running: `systemctl status postgresql`
- Check firewall allows port 5432
- Check `postgresql.conf` has `listen_addresses = '*'`

**Error: "authentication failed"**
- Verify username and password in `DATABASE_URL`
- Check `pg_hba.conf` has entry for your app server IP

**Error: "database does not exist"**
- Create database: `CREATE DATABASE hr_testing;`

### LDAP Connection Issues

**Error: "LDAP server unreachable"**
- Check LDAP_HOST is correct
- Ping LDAP server: `ping LDAP_HOST`
- Check firewall allows port 389/636
- Verify network connectivity

**Error: "Invalid credentials"**
- Verify LDAP_DOMAIN is correct
- Verify LDAP_BASE_DN is correct
- Test with known working employee credentials

**Error: "Access denied"**
- Check employee ID is in `PERMITTED_USERS`
- Verify whitelist format is correct (no extra spaces!)

---

## 📞 Getting Help

**For PostgreSQL issues:**
- Check database server logs
- Ask your database administrator

**For LDAP issues:**
- Check `login_history.log` for detailed errors
- Ask your IT department to verify LDAP settings

**For application issues:**
- Check application logs
- Verify `.env` file is correctly configured
- Ensure all dependencies installed

---

**Last Updated:** 2025-01-11
**Your Path:** `/home/ocds_mukhtar/00061221/hr_testing`
