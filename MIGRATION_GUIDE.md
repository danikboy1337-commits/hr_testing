# 🚀 HR Testing Platform - Local Server Migration Guide

**Target Environment:** Ubuntu Server (Internal Network Only)
**Database:** PostgreSQL (Separate Server)
**Authentication:** LDAP/Active Directory with TLS
**Process Manager:** systemd
**Estimated Time:** 2-3 days

---

## 📋 Table of Contents

1. [Pre-Migration Checklist](#1-pre-migration-checklist)
2. [Server Preparation](#2-server-preparation)
3. [Database Setup (PostgreSQL Server)](#3-database-setup-postgresql-server)
4. [Application Installation](#4-application-installation)
5. [LDAP Configuration](#5-ldap-configuration)
6. [Service Configuration (systemd)](#6-service-configuration-systemd)
7. [Testing & Validation](#7-testing--validation)
8. [nginx Setup (Optional - For Future)](#8-nginx-setup-optional---for-future)
9. [Monitoring & Maintenance](#9-monitoring--maintenance)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Pre-Migration Checklist

### 1.1 Information Gathering

Collect the following information before starting:

#### ✅ PostgreSQL Database Server
- [ ] Database server IP address/hostname: `___________________`
- [ ] Database port (default: 5432): `___________________`
- [ ] Database name to create: `hr_testing` (recommended)
- [ ] Database username: `___________________`
- [ ] Database password: `___________________`
- [ ] Verify network connectivity from app server to DB server

#### ✅ LDAP/Active Directory
- [ ] LDAP server hostname/IP: `___________________`
- [ ] LDAP port (389 for LDAP, 636 for LDAPS): `___________________`
- [ ] Using TLS: **Yes** ✓
- [ ] Domain name (e.g., `HALYKBANK`): `___________________`
- [ ] Base DN (e.g., `OU=Employees,DC=halykbank,DC=kz`): `___________________`
- [ ] Test employee ID and password for verification

#### ✅ Employee Whitelist (from HR Department)
Format: `EMPLOYEE_ID:Full Name:role:permissions`

Example:
```
00058215:Nadir Sultanov:hr:read,write,admin
00037099:Saltanat Kenzhebekova:hr:read,write,admin
00012345:Test Manager:manager:read,write
00067890:Test Employee:employee:read
```

- [ ] Employee whitelist prepared: `___________________`

#### ✅ Application Server
- [ ] Server IP address: `___________________`
- [ ] Ubuntu version: `___________________` (should be 20.04+ or 22.04+)
- [ ] Python version: `python3 --version` (should be 3.11+)
- [ ] Server accessible via SSH: `ssh username@server-ip`
- [ ] Have sudo/root access: Yes/No

#### ✅ Network & Firewall
- [ ] App server can reach PostgreSQL server on port 5432
- [ ] App server can reach LDAP server on port 389/636
- [ ] Application port chosen (default: 8000): `___________________`
- [ ] Internal users can reach app server on chosen port

### 1.2 Download Project Files

On your local machine, ensure you have the latest code:

```bash
git pull origin claude/analyze-competency-project-011CUzACSFZVUJLc3EVjkJog
```

**Files to transfer to server:**
- All application code (main.py, config.py, auth.py, ldap.py, etc.)
- `requirements.txt`
- `db/` directory (database scripts)
- `static/` directory (images, assets)
- `templates/` directory (HTML templates)
- `specializations/` directory (competency data)
- `Questions.json` (test questions)
- `.env.template` (will create `.env` from this)

---

## 2. Server Preparation

### 2.1 Connect to Server

```bash
ssh your-username@YOUR_SERVER_IP
```

### 2.2 Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### 2.3 Install Required System Packages

```bash
# Install Python 3.11 and pip
sudo apt install python3.11 python3.11-venv python3.11-dev python3-pip -y

# Install PostgreSQL client (for database connectivity)
sudo apt install postgresql-client libpq-dev -y

# Install LDAP client libraries
sudo apt install libldap2-dev libsasl2-dev -y

# Install build essentials (for Python package compilation)
sudo apt install build-essential -y

# Install git (if not already installed)
sudo apt install git -y

# Optional: Install nginx (for future use)
# sudo apt install nginx -y
```

### 2.4 Verify Python Version

```bash
python3.11 --version
# Should output: Python 3.11.x
```

If Python 3.11 is not available, you may need to add deadsnakes PPA:

```bash
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev -y
```

### 2.5 Create Application User (Security Best Practice)

```bash
# Create dedicated user for running the application
sudo useradd -m -s /bin/bash hrapp

# Set password for the user (optional)
sudo passwd hrapp
```

### 2.6 Create Application Directory

```bash
# Create directory for the application
sudo mkdir -p /opt/hr_testing

# Change ownership to hrapp user
sudo chown -R hrapp:hrapp /opt/hr_testing

# Create logs directory
sudo mkdir -p /var/log/hr_testing
sudo chown -R hrapp:hrapp /var/log/hr_testing
```

---

## 3. Database Setup (PostgreSQL Server)

### 3.1 Connect to PostgreSQL Server

On your **PostgreSQL database server**, connect as postgres superuser:

```bash
# If you're on the same server as PostgreSQL
sudo -u postgres psql

# If PostgreSQL is on a different server, connect via SSH first
ssh your-username@POSTGRESQL_SERVER_IP
sudo -u postgres psql
```

### 3.2 Create Database and User

```sql
-- Create database
CREATE DATABASE hr_testing;

-- Create user (replace 'your_password_here' with a strong password)
CREATE USER hrapp WITH PASSWORD 'your_password_here';

-- Grant all privileges on the database
GRANT ALL PRIVILEGES ON DATABASE hr_testing TO hrapp;

-- Connect to the database
\c hr_testing

-- Grant schema privileges
GRANT ALL PRIVILEGES ON SCHEMA public TO hrapp;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO hrapp;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO hrapp;

-- Ensure future tables also have correct privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO hrapp;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO hrapp;

-- Verify connection
\l hr_testing
\q
```

### 3.3 Configure PostgreSQL for Remote Connections

If your application server and database server are separate, configure PostgreSQL to accept remote connections:

**On PostgreSQL server:**

1. Edit `postgresql.conf`:
```bash
sudo nano /etc/postgresql/14/main/postgresql.conf
# (Path may vary: use /etc/postgresql/*/main/postgresql.conf)
```

Find and modify:
```conf
listen_addresses = '*'  # or specific IP of app server
```

2. Edit `pg_hba.conf`:
```bash
sudo nano /etc/postgresql/14/main/pg_hba.conf
```

Add line (replace `APP_SERVER_IP` with your application server's IP):
```conf
# Allow hrapp user from application server
host    hr_testing    hrapp    APP_SERVER_IP/32    md5
```

3. Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

### 3.4 Test Database Connection from Application Server

From your **application server**:

```bash
psql -h POSTGRESQL_SERVER_IP -p 5432 -U hrapp -d hr_testing
# Enter the password when prompted
# If successful, you'll see: hr_testing=>
\q
```

**If connection fails**, check:
- Firewall on PostgreSQL server allows port 5432 from app server
- `postgresql.conf` has correct `listen_addresses`
- `pg_hba.conf` has entry for app server IP

---

## 4. Application Installation

### 4.1 Transfer Application Files to Server

**Option A: Using Git (Recommended)**

On the **application server**, as `hrapp` user:

```bash
sudo -u hrapp -i
cd /opt/hr_testing

# Clone repository (if accessible from server)
git clone https://github.com/YOUR_ORG/hr_testing.git .

# Or clone the specific branch
git clone -b claude/analyze-competency-project-011CUzACSFZVUJLc3EVjkJog https://github.com/YOUR_ORG/hr_testing.git .
```

**Option B: Using SCP (From Your Local Machine)**

```bash
# From your local machine where you have the code
scp -r /path/to/hr_testing/* your-username@YOUR_SERVER_IP:/tmp/hr_testing/

# Then on the server
sudo mv /tmp/hr_testing/* /opt/hr_testing/
sudo chown -R hrapp:hrapp /opt/hr_testing
```

**Option C: Using rsync (Recommended for large files)**

```bash
# From your local machine
rsync -avz --progress /path/to/hr_testing/ your-username@YOUR_SERVER_IP:/tmp/hr_testing/

# Then on the server
sudo mv /tmp/hr_testing/* /opt/hr_testing/
sudo chown -R hrapp:hrapp /opt/hr_testing
```

### 4.2 Verify All Files Are Present

```bash
sudo -u hrapp -i
cd /opt/hr_testing

ls -la
# Should see:
# main.py, config.py, auth.py, ldap.py, requirements.txt
# db/, static/, templates/, specializations/
# Questions.json, .env.template, etc.
```

### 4.3 Create Python Virtual Environment

```bash
sudo -u hrapp -i
cd /opt/hr_testing

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 4.4 Install Python Dependencies

```bash
# Ensure virtual environment is activated (you should see (venv) in prompt)
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt

# This will install:
# - fastapi, uvicorn, gunicorn
# - psycopg (PostgreSQL driver)
# - ldap3 (LDAP authentication)
# - anthropic (Claude API - optional, not needed for your deployment)
# - and all other dependencies
```

**Verify installation:**

```bash
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "import psycopg; print(f'psycopg: {psycopg.__version__}')"
python -c "import ldap3; print(f'ldap3: {ldap3.__version__}')"
```

### 4.5 Create Environment Configuration File

```bash
cd /opt/hr_testing

# Copy template to create .env file
cp .env.template .env

# Edit .env with real configuration
nano .env
```

**Configure `.env` file with your actual values:**

```bash
# ============================================
# DATABASE CONFIGURATION
# ============================================
DATABASE_URL=postgresql://hrapp:YOUR_DB_PASSWORD@POSTGRESQL_SERVER_IP:5432/hr_testing

# ============================================
# LDAP/ACTIVE DIRECTORY AUTHENTICATION
# ============================================
LDAP_ENABLED=True

# LDAP Server Configuration
LDAP_DOMAIN=YOUR_DOMAIN          # Example: HALYKBANK
LDAP_HOST=YOUR_LDAP_SERVER_IP    # Example: 10.20.30.40 or ad.company.local
LDAP_PORT=389                     # 389 for LDAP, 636 for LDAPS
LDAP_BASE_DN=YOUR_BASE_DN        # Example: OU=Employees,DC=halykbank,DC=kz
LDAP_USE_SSL=False                # True if using port 636
LDAP_USE_TLS=True                 # True for STARTTLS (recommended)
LDAP_TIMEOUT=10

# ============================================
# PERMITTED USERS WHITELIST
# ============================================
# Format: EMPLOYEE_ID:NAME:ROLE:PERMISSIONS;EMPLOYEE_ID:NAME:ROLE:PERMISSIONS
# Roles: hr, manager, employee
# Permissions: read, write, admin (comma-separated)
PERMITTED_USERS=00058215:Nadir Sultanov:hr:read,write,admin;00037099:Saltanat Kenzhebekova:hr:read,write,admin

# ============================================
# JWT SECURITY
# ============================================
# Generate strong secret key with: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET_KEY=GENERATE_NEW_SECRET_HERE

# ============================================
# APPLICATION SETTINGS
# ============================================
HOST=0.0.0.0
PORT=8000
DEBUG=False

# ============================================
# ANTHROPIC CLAUDE API (OPTIONAL - NOT NEEDED)
# ============================================
# You can leave this empty or comment it out
# ANTHROPIC_API_KEY=

# ============================================
# RECAPTCHA (OPTIONAL - NOT CONFIGURED)
# ============================================
# RECAPTCHA_SITE_KEY=
# RECAPTCHA_SECRET_KEY=
```

**Generate JWT Secret Key:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy output and paste into JWT_SECRET_KEY
```

**Set secure file permissions:**

```bash
chmod 600 .env
chown hrapp:hrapp .env
```

### 4.6 Initialize Database Schema

```bash
cd /opt/hr_testing
source venv/bin/activate

# 1. Create all tables
python db/create_tables.py

# Expected output:
# ✅ Successfully created all tables

# 2. Run initial migration (adds roles and departments)
python db/run_migration.py db/migration_add_roles_departments.sql

# Expected output:
# ✅ Migration completed successfully

# 3. Run additional migrations
python db/run_migration.py db/migrations/add_test_time_limit.sql
python db/run_migration.py db/migrations/update_manager_evaluations_competency_based.sql

# Expected output:
# ✅ Migration completed successfully (for each)
```

### 4.7 Load Application Data

```bash
cd /opt/hr_testing
source venv/bin/activate

# 1. Load test questions (~3000 questions)
python db/load_questions.py

# Expected output:
# Loading questions from Questions.json...
# ✅ Loaded X questions successfully

# 2. Load specializations and competencies
python db/import_specializations.py

# Expected output:
# Loading specializations from specializations/output/final/...
# ✅ Loaded 17 specializations successfully
```

**Verify data loaded:**

```bash
psql -h POSTGRESQL_SERVER_IP -U hrapp -d hr_testing -c "SELECT COUNT(*) FROM questions;"
# Should show ~3000 questions

psql -h POSTGRESQL_SERVER_IP -U hrapp -d hr_testing -c "SELECT COUNT(*) FROM specializations;"
# Should show 17 specializations

psql -h POSTGRESQL_SERVER_IP -U hrapp -d hr_testing -c "SELECT name FROM departments;"
# Should show 8 departments
```

---

## 5. LDAP Configuration

### 5.1 Test LDAP Connectivity

Create a test script:

```bash
cd /opt/hr_testing
nano test_ldap_connection.py
```

Paste this content:

```python
#!/usr/bin/env python3
"""Test LDAP connection and authentication"""
import sys
sys.path.append('.')

from dotenv import load_dotenv
load_dotenv()

from ldap import check_ldap_password, LDAP_CONFIG

print("=" * 70)
print("🔍 TESTING LDAP CONNECTION")
print("=" * 70)
print(f"LDAP Server: {LDAP_CONFIG['host']}:{LDAP_CONFIG['port']}")
print(f"Domain: {LDAP_CONFIG['domain']}")
print(f"Base DN: {LDAP_CONFIG['base_dn']}")
print(f"Use TLS: {LDAP_CONFIG['use_tls']}")
print(f"Use SSL: {LDAP_CONFIG['use_ssl']}")
print("=" * 70)
print()

# Test with a real employee ID and password
TEST_EMPLOYEE_ID = input("Enter test employee ID: ")
TEST_PASSWORD = input("Enter test password: ")

try:
    result = check_ldap_password(TEST_EMPLOYEE_ID, TEST_PASSWORD)

    if result:
        print()
        print("=" * 70)
        print("✅ SUCCESS! LDAP authentication working")
        print("=" * 70)
        print("LDAP server is reachable and authentication is functional.")
    else:
        print()
        print("=" * 70)
        print("❌ AUTHENTICATION FAILED")
        print("=" * 70)
        print("Possible reasons:")
        print("  - Wrong employee ID or password")
        print("  - Account locked/disabled in Active Directory")
        print("  - Password expired")
except Exception as e:
    print()
    print("=" * 70)
    print("❌ LDAP CONNECTION ERROR")
    print("=" * 70)
    print(f"Error: {e}")
    print()
    print("Possible reasons:")
    print("  - LDAP server hostname/IP incorrect")
    print("  - Port blocked by firewall")
    print("  - Domain name incorrect")
    print("  - Base DN incorrect")
    print("  - Network connectivity issue")
    print()
    print("Check login_history.log for detailed error messages")

print()
print("💡 Check login_history.log for detailed logs")
```

Save and run:

```bash
source venv/bin/activate
python test_ldap_connection.py
```

Enter a valid employee ID and password from your company's Active Directory.

**Expected output (success):**
```
✅ SUCCESS! LDAP authentication working
```

**If it fails:**
- Check `login_history.log` for detailed error messages
- Verify LDAP_HOST, LDAP_PORT, LDAP_DOMAIN, LDAP_BASE_DN in `.env`
- Ensure firewall allows connection to LDAP server
- Verify TLS settings match your AD configuration

### 5.2 Verify Whitelist Configuration

Test that your whitelist is properly formatted:

```bash
cd /opt/hr_testing
source venv/bin/activate

python -c "from ldap import PERMITTED_USERS; print('Permitted Users:'); [print(f'{k}: {v}') for k,v in PERMITTED_USERS.items()]"
```

**Expected output:**
```
Permitted Users:
00058215: {'name': 'Nadir Sultanov', 'role': 'hr', 'permissions': ['read', 'write', 'admin']}
00037099: {'name': 'Saltanat Kenzhebekova', 'role': 'hr', 'permissions': ['read', 'write', 'admin']}
...
```

---

## 6. Service Configuration (systemd)

### 6.1 Create systemd Service File

Create the service configuration:

```bash
sudo nano /etc/systemd/system/hr-testing.service
```

Paste this configuration:

```ini
[Unit]
Description=HR Testing Platform - Halyk Bank
Documentation=https://github.com/YOUR_ORG/hr_testing
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=notify
User=hrapp
Group=hrapp
WorkingDirectory=/opt/hr_testing
Environment="PATH=/opt/hr_testing/venv/bin:/usr/local/bin:/usr/bin:/bin"

# Load environment variables from .env file
EnvironmentFile=/opt/hr_testing/.env

# Start application with Gunicorn + Uvicorn workers
# Workers: 4 (adjust based on your needs - you have 128 CPUs!)
# Timeout: 120 seconds (for Claude API calls, though not needed now)
# Bind to all interfaces on port 8000
ExecStart=/opt/hr_testing/venv/bin/gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile /var/log/hr_testing/access.log \
    --error-logfile /var/log/hr_testing/error.log \
    --log-level info

# Restart policy
Restart=always
RestartSec=10

# Security hardening (optional but recommended)
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/hr_testing /var/log/hr_testing

# Resource limits (adjust as needed)
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
```

**Note on workers:** You have 128 CPUs! You can increase workers if needed. Formula: `(2 x CPU cores) + 1`. But start with 4-8 workers and monitor.

### 6.2 Enable and Start Service

```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable hr-testing.service

# Start the service now
sudo systemctl start hr-testing.service

# Check status
sudo systemctl status hr-testing.service
```

**Expected output:**
```
● hr-testing.service - HR Testing Platform - Halyk Bank
     Loaded: loaded (/etc/systemd/system/hr-testing.service; enabled)
     Active: active (running) since ...
```

### 6.3 Verify Application is Running

```bash
# Check if process is running
ps aux | grep gunicorn

# Check if application is listening on port 8000
sudo netstat -tlnp | grep 8000
# Or: sudo ss -tlnp | grep 8000

# Test health endpoint
curl http://localhost:8000/health

# Expected output:
# {"status":"healthy"}
```

### 6.4 View Application Logs

```bash
# View real-time logs
sudo journalctl -u hr-testing.service -f

# View last 100 lines
sudo journalctl -u hr-testing.service -n 100

# View logs since today
sudo journalctl -u hr-testing.service --since today

# View error logs only
sudo tail -f /var/log/hr_testing/error.log

# View access logs
sudo tail -f /var/log/hr_testing/access.log

# View LDAP authentication logs
sudo -u hrapp tail -f /opt/hr_testing/login_history.log
```

### 6.5 Common systemd Commands

```bash
# Start service
sudo systemctl start hr-testing.service

# Stop service
sudo systemctl stop hr-testing.service

# Restart service (after configuration changes)
sudo systemctl restart hr-testing.service

# Reload application (graceful restart)
sudo systemctl reload hr-testing.service

# Check status
sudo systemctl status hr-testing.service

# Disable auto-start on boot
sudo systemctl disable hr-testing.service

# Enable auto-start on boot
sudo systemctl enable hr-testing.service
```

---

## 7. Testing & Validation

### 7.1 Test From Server (Localhost)

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test login page loads
curl http://localhost:8000/login

# Test API endpoint (should return 401 without token)
curl http://localhost:8000/api/specializations
```

### 7.2 Test From Your Computer (Internal Network)

Open your web browser and navigate to:

```
http://YOUR_SERVER_IP:8000/login
```

**You should see:**
- Halyk Bank branded login page
- Employee ID and password fields
- LDAP status indicator showing "✅ LDAP активирован"

### 7.3 Test Authentication Flow

**Test Case 1: Valid Employee Login**

1. Enter a whitelisted employee ID (from `PERMITTED_USERS`)
2. Enter correct Active Directory password
3. Click "Войти в систему"

**Expected result:**
- ✅ Redirected to appropriate dashboard based on role:
  - HR role → `/hr/menu`
  - Manager role → `/manager/menu`
  - Employee role → `/specializations`

**Test Case 2: Invalid Password**

1. Enter valid employee ID
2. Enter wrong password
3. Click "Войти в систему"

**Expected result:**
- ❌ Error message: "The username or password you have entered is incorrect."
- Check `login_history.log` for failed attempt

**Test Case 3: Non-Whitelisted Employee**

1. Enter employee ID NOT in `PERMITTED_USERS`
2. Enter any password
3. Click "Войти в систему"

**Expected result:**
- ❌ Error message: "Доступ к ресурсу отсутствует"
- Check `login_history.log` for access denied

### 7.4 Test Key Functionalities

**For HR Users:**
1. Login as HR
2. Navigate to `/hr/menu`
3. Click "Управление профилями" - should load profiles
4. Click "Просмотр всех сотрудников" - should show employee list
5. Click "Оценка сотрудников" - should show evaluation interface

**For Manager Users:**
1. Login as Manager
2. Navigate to `/manager/menu`
3. View employees in your department
4. Try rating an employee's competencies
5. Verify ratings are saved

**For Employee Users:**
1. Login as Employee
2. Select a specialization
3. Start a test
4. Verify timer works (40 minutes)
5. Answer questions
6. Submit test
7. Check results

### 7.5 Test Database Connectivity

```bash
# From application server
psql -h POSTGRESQL_SERVER_IP -U hrapp -d hr_testing

# Check some data
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM questions;
SELECT COUNT(*) FROM specializations;

\q
```

### 7.6 Check Logs for Errors

```bash
# Application logs
sudo journalctl -u hr-testing.service --since "10 minutes ago" | grep -i error

# Error log file
sudo tail -100 /var/log/hr_testing/error.log

# LDAP authentication log
sudo -u hrapp tail -50 /opt/hr_testing/login_history.log
```

**No errors should appear** during normal operation.

### 7.7 Performance Test (Optional)

With your massive resources (1TB RAM, 128 CPUs), the application should handle load easily:

```bash
cd /opt/hr_testing
source venv/bin/activate

# Install load testing tool
pip install locust

# Run load test (included in repository)
locust -f locustfile.py --host http://localhost:8000
```

Open browser to: `http://YOUR_SERVER_IP:8089`

- Start with 10 users
- Spawn rate: 1 user/second
- Monitor response times

**Expected performance:**
- Response time: <100ms for most endpoints
- 0 failures
- Can handle 100+ concurrent users easily

---

## 8. nginx Setup (Optional - For Future)

When you're ready to set up a domain name and use nginx as reverse proxy:

### 8.1 Install nginx

```bash
sudo apt install nginx -y
```

### 8.2 Create nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/hr-testing
```

Paste this configuration:

```nginx
# HTTP (port 80) - Redirect to HTTPS (if using SSL)
# For now, just serve HTTP
server {
    listen 80;
    server_name hr.company.local;  # Replace with your domain

    # Client max body size (for file uploads)
    client_max_body_size 10M;

    # Access and error logs
    access_log /var/log/nginx/hr-testing-access.log;
    error_log /var/log/nginx/hr-testing-error.log;

    # Static files (served directly by nginx for better performance)
    location /static/ {
        alias /opt/hr_testing/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Application (proxy to Gunicorn)
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed in future)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}

# HTTPS (port 443) - For future use with SSL certificate
# Uncomment when you have SSL certificate
# server {
#     listen 443 ssl http2;
#     server_name hr.company.local;
#
#     ssl_certificate /etc/ssl/certs/hr-testing.crt;
#     ssl_certificate_key /etc/ssl/private/hr-testing.key;
#     ssl_protocols TLSv1.2 TLSv1.3;
#     ssl_ciphers HIGH:!aNULL:!MD5;
#
#     client_max_body_size 10M;
#     access_log /var/log/nginx/hr-testing-access.log;
#     error_log /var/log/nginx/hr-testing-error.log;
#
#     location /static/ {
#         alias /opt/hr_testing/static/;
#         expires 30d;
#         add_header Cache-Control "public, immutable";
#     }
#
#     location / {
#         proxy_pass http://127.0.0.1:8000;
#         proxy_set_header Host $host;
#         proxy_set_header X-Real-IP $remote_addr;
#         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#         proxy_set_header X-Forwarded-Proto $scheme;
#         proxy_http_version 1.1;
#         proxy_set_header Upgrade $http_upgrade;
#         proxy_set_header Connection "upgrade";
#         proxy_connect_timeout 60s;
#         proxy_send_timeout 60s;
#         proxy_read_timeout 60s;
#     }
# }
```

### 8.3 Enable nginx Configuration

```bash
# Create symbolic link to enable site
sudo ln -s /etc/nginx/sites-available/hr-testing /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx
```

### 8.4 Access via nginx

Now you can access the application via nginx (port 80):

```
http://YOUR_SERVER_IP/
# or
http://hr.company.local/  (if DNS configured)
```

---

## 9. Monitoring & Maintenance

### 9.1 Set Up Log Rotation

Prevent logs from consuming too much disk space:

```bash
sudo nano /etc/logrotate.d/hr-testing
```

Paste:

```
/var/log/hr_testing/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 hrapp hrapp
    sharedscripts
    postrotate
        systemctl reload hr-testing.service > /dev/null 2>&1 || true
    endscript
}

/opt/hr_testing/login_history.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 hrapp hrapp
    maxsize 10M
}
```

Test log rotation:

```bash
sudo logrotate -f /etc/logrotate.d/hr-testing
```

### 9.2 Database Backup Script

Create automated backup script:

```bash
sudo nano /opt/hr_testing/backup_database.sh
```

Paste:

```bash
#!/bin/bash
# Database backup script for HR Testing Platform

# Configuration
DB_HOST="POSTGRESQL_SERVER_IP"
DB_PORT="5432"
DB_NAME="hr_testing"
DB_USER="hrapp"
BACKUP_DIR="/backup/hr_testing"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/hr_testing_$DATE.sql"
LOG_FILE="/var/log/hr_testing/backup.log"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Log start
echo "$(date): Starting backup..." >> $LOG_FILE

# Perform backup
PGPASSWORD="YOUR_DB_PASSWORD" pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME > $BACKUP_FILE

# Check if backup succeeded
if [ $? -eq 0 ]; then
    # Compress backup
    gzip $BACKUP_FILE
    echo "$(date): Backup completed successfully: ${BACKUP_FILE}.gz" >> $LOG_FILE

    # Delete backups older than 30 days
    find $BACKUP_DIR -name "hr_testing_*.sql.gz" -mtime +30 -delete
    echo "$(date): Old backups cleaned up" >> $LOG_FILE
else
    echo "$(date): Backup FAILED!" >> $LOG_FILE
fi
```

Make executable:

```bash
sudo chmod +x /opt/hr_testing/backup_database.sh
sudo chown hrapp:hrapp /opt/hr_testing/backup_database.sh
```

Create backup directory:

```bash
sudo mkdir -p /backup/hr_testing
sudo chown hrapp:hrapp /backup/hr_testing
```

Test backup:

```bash
sudo -u hrapp /opt/hr_testing/backup_database.sh
ls -lh /backup/hr_testing/
```

### 9.3 Automate Backups with Cron

```bash
sudo crontab -e -u hrapp
```

Add this line (backup daily at 2 AM):

```cron
0 2 * * * /opt/hr_testing/backup_database.sh
```

### 9.4 Health Check Monitoring

Create health check script:

```bash
sudo nano /opt/hr_testing/health_check.sh
```

Paste:

```bash
#!/bin/bash
# Health check script

URL="http://localhost:8000/health"
EXPECTED="healthy"
LOG_FILE="/var/log/hr_testing/health_check.log"

# Perform health check
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $URL)

if [ $RESPONSE -eq 200 ]; then
    echo "$(date): ✅ Health check passed (HTTP $RESPONSE)" >> $LOG_FILE
else
    echo "$(date): ❌ Health check FAILED (HTTP $RESPONSE)" >> $LOG_FILE

    # Optional: Send alert email or restart service
    # systemctl restart hr-testing.service
fi
```

Make executable:

```bash
sudo chmod +x /opt/hr_testing/health_check.sh
```

Add to cron (check every 5 minutes):

```bash
sudo crontab -e
```

Add:

```cron
*/5 * * * * /opt/hr_testing/health_check.sh
```

### 9.5 Disk Space Monitoring

```bash
# Check disk usage
df -h

# Check specific directories
du -sh /opt/hr_testing
du -sh /var/log/hr_testing
du -sh /backup/hr_testing

# Monitor database size
psql -h POSTGRESQL_SERVER_IP -U hrapp -d hr_testing -c "SELECT pg_size_pretty(pg_database_size('hr_testing'));"
```

---

## 10. Troubleshooting

### 10.1 Application Won't Start

**Symptoms:** `systemctl status hr-testing.service` shows "failed"

**Diagnosis:**
```bash
# Check detailed error logs
sudo journalctl -u hr-testing.service -n 100 --no-pager

# Check error log file
sudo tail -50 /var/log/hr_testing/error.log
```

**Common causes:**

1. **Database connection error**
   - Verify `DATABASE_URL` in `.env`
   - Test connection: `psql -h HOST -U hrapp -d hr_testing`
   - Check PostgreSQL is running: `systemctl status postgresql`

2. **Port already in use**
   - Check: `sudo netstat -tlnp | grep 8000`
   - Kill process: `sudo kill -9 PID`
   - Or change PORT in `.env`

3. **Python dependencies missing**
   - Reinstall: `pip install -r requirements.txt`

4. **Permission errors**
   - Check ownership: `ls -la /opt/hr_testing`
   - Fix: `sudo chown -R hrapp:hrapp /opt/hr_testing`

### 10.2 LDAP Authentication Not Working

**Symptoms:** Login fails with "LDAP authentication is not configured" or connection errors

**Diagnosis:**
```bash
# Run LDAP test script
cd /opt/hr_testing
source venv/bin/activate
python test_ldap_connection.py

# Check LDAP logs
tail -50 login_history.log
```

**Common causes:**

1. **LDAP_ENABLED=False**
   - Check `.env`: `grep LDAP_ENABLED .env`
   - Set to: `LDAP_ENABLED=True`
   - Restart service

2. **Wrong LDAP server/port**
   - Test connection: `telnet LDAP_HOST 389`
   - Or: `nc -zv LDAP_HOST 389`
   - Check firewall rules

3. **Incorrect Base DN or Domain**
   - Verify with IT department
   - Check `login_history.log` for detailed error

4. **TLS/SSL misconfiguration**
   - Try `LDAP_USE_TLS=False` temporarily
   - Check if server requires TLS: ask IT

### 10.3 Database Queries Slow

**Symptoms:** Pages load slowly, timeouts

**Diagnosis:**
```bash
# Check database connections
psql -h HOST -U hrapp -d hr_testing -c "SELECT count(*) FROM pg_stat_activity WHERE datname='hr_testing';"

# Check slow queries (if PostgreSQL logging enabled)
psql -h HOST -U hrapp -d hr_testing -c "SELECT query, calls, total_time/1000 as total_seconds FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

**Solutions:**

1. **Increase connection pool**
   - Edit `main.py`, increase `max_size` in connection pool
   - Restart service

2. **Analyze queries**
   - Check if indexes are being used
   - Run `ANALYZE` on tables

3. **Restart PostgreSQL**
   - On DB server: `sudo systemctl restart postgresql`

### 10.4 High Memory/CPU Usage

**Symptoms:** Server running slow, out of memory

**Diagnosis:**
```bash
# Check resource usage
top
# Or: htop

# Check HR Testing process
ps aux | grep gunicorn

# Check memory
free -h

# Check disk
df -h
```

**Solutions:**

1. **Reduce number of workers**
   - Edit `/etc/systemd/system/hr-testing.service`
   - Change `--workers 4` to `--workers 2`
   - Reload: `sudo systemctl daemon-reload`
   - Restart: `sudo systemctl restart hr-testing.service`

2. **Check for memory leaks**
   - Monitor over time
   - Restart service periodically if needed

3. **Optimize database queries**
   - Review slow queries
   - Add indexes where needed

### 10.5 Users Can't Access Application

**Symptoms:** Browser shows "Connection refused" or timeout

**Diagnosis:**
```bash
# Check if application is running
systemctl status hr-testing.service

# Check if listening on port
sudo netstat -tlnp | grep 8000

# Check from server
curl http://localhost:8000/health

# Check firewall
sudo ufw status  # If UFW is enabled
sudo iptables -L -n  # Check iptables rules
```

**Solutions:**

1. **Service not running**
   - Start: `sudo systemctl start hr-testing.service`

2. **Firewall blocking**
   - Allow port: `sudo ufw allow 8000`
   - Or: `sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT`

3. **Wrong IP/port**
   - Verify `.env` has `HOST=0.0.0.0`
   - Verify `PORT=8000`

4. **Network issue**
   - Check routing from client to server
   - Verify server IP is correct

### 10.6 Logs Growing Too Large

**Symptoms:** Disk space running out

**Diagnosis:**
```bash
# Check log sizes
du -sh /var/log/hr_testing/*
du -sh /opt/hr_testing/login_history.log

# Check disk usage
df -h
```

**Solutions:**

1. **Enable log rotation** (see section 9.1)

2. **Manually clean old logs**
   ```bash
   sudo find /var/log/hr_testing -name "*.log" -mtime +30 -delete
   ```

3. **Compress old logs**
   ```bash
   gzip /var/log/hr_testing/*.log.1
   ```

### 10.7 Getting Help

If you encounter issues not covered here:

1. **Check application logs:**
   ```bash
   sudo journalctl -u hr-testing.service -f
   ```

2. **Check LDAP logs:**
   ```bash
   tail -f /opt/hr_testing/login_history.log
   ```

3. **Check database connectivity:**
   ```bash
   psql -h HOST -U hrapp -d hr_testing
   ```

4. **Run health check:**
   ```bash
   curl http://localhost:8000/health
   ```

5. **Gather debugging info:**
   ```bash
   # System info
   uname -a
   python3.11 --version

   # Application info
   systemctl status hr-testing.service
   sudo netstat -tlnp | grep 8000

   # Logs
   sudo journalctl -u hr-testing.service -n 100 --no-pager > debug.log
   ```

---

## 📊 Migration Checklist Summary

### Pre-Migration
- [ ] Collected all server IPs, credentials, configurations
- [ ] Prepared PostgreSQL database server
- [ ] Obtained LDAP server details from IT
- [ ] Got employee whitelist from HR
- [ ] Generated JWT secret key

### Installation
- [ ] Updated Ubuntu system
- [ ] Installed Python 3.11, PostgreSQL client, LDAP libraries
- [ ] Created `hrapp` user
- [ ] Created application directory `/opt/hr_testing`
- [ ] Transferred application files to server
- [ ] Created Python virtual environment
- [ ] Installed Python dependencies
- [ ] Created and configured `.env` file

### Database
- [ ] Created PostgreSQL database and user
- [ ] Configured remote connections (if needed)
- [ ] Tested database connectivity
- [ ] Ran database initialization scripts
- [ ] Loaded questions and specializations data
- [ ] Verified data loaded correctly

### LDAP
- [ ] Configured LDAP settings in `.env`
- [ ] Set `LDAP_ENABLED=True`
- [ ] Configured employee whitelist
- [ ] Tested LDAP connectivity
- [ ] Verified authentication works

### Service
- [ ] Created systemd service file
- [ ] Enabled and started service
- [ ] Verified application is running
- [ ] Tested health endpoint

### Testing
- [ ] Tested login with valid credentials
- [ ] Tested login with invalid credentials
- [ ] Tested non-whitelisted employee access
- [ ] Tested HR functionality
- [ ] Tested Manager functionality
- [ ] Tested Employee functionality
- [ ] Verified all logs are clean

### Production Setup
- [ ] Set up log rotation
- [ ] Created database backup script
- [ ] Automated backups with cron
- [ ] Set up health monitoring
- [ ] Documented server configuration

### Optional (Future)
- [ ] Installed and configured nginx
- [ ] Obtained SSL certificate
- [ ] Configured domain name
- [ ] Set up advanced monitoring

---

## 🎉 Congratulations!

If you've completed all steps, your HR Testing Platform is now running on your local company server!

**Access the application:**
```
http://YOUR_SERVER_IP:8000/login
```

**Next steps:**
1. Train HR staff on using the platform
2. Monitor logs for any issues in first few days
3. Set up regular database backups
4. Plan for nginx + domain name setup
5. Consider load testing with expected user count

**Support:**
- Check `LDAP_SETUP.md` for detailed LDAP troubleshooting
- Check `TESTING_GUIDE.md` for testing procedures
- Review logs regularly: `sudo journalctl -u hr-testing.service -f`

---

**Document Version:** 1.0
**Last Updated:** 2025-01-11
**Author:** Development Team
