# 🔐 LDAP Authentication Setup Guide

## Overview

The HR Testing Platform now uses **LDAP/Active Directory authentication** instead of phone-based authentication. This provides enterprise-grade security by:

✅ Authenticating against company's Active Directory
✅ Requiring employees to be whitelisted
✅ Auto-creating user accounts on first login
✅ Centralized user management
✅ Complete audit trail via logging

---

## 🎯 Current Status

**LDAP Status**: ⚠️ **NOT ACTIVATED** (using placeholder values)

The system is configured with **placeholder/temporary values** and will not connect to a real LDAP server until you activate it with real configuration.

---

## 📋 Prerequisites

Before activating LDAP, you need:

### 1. **LDAP Server Information** (from IT Department)
- LDAP server hostname or IP address
- Windows domain name
- Organizational Unit (OU) path
- Port number (usually 389 for LDAP, 636 for LDAPS)
- Test employee credentials

### 2. **Employee Whitelist** (from HR Department)
- List of employee IDs allowed to access the platform
- Their full names
- Their roles (hr/manager/employee)

### 3. **Strong JWT Secret**
- Generate a cryptographically secure secret key

---

## 🚀 Activation Steps

### Step 1: Install Dependencies

```bash
pip install ldap3
```

Verify installation:
```bash
python -c "import ldap3; print('✅ ldap3 installed successfully')"
```

### Step 2: Get Configuration from IT Department

Contact your IT department and ask for:

1. **LDAP Server Details:**
   - What is the LDAP server hostname?
   - What is the Windows domain name?
   - What is the Base DN (Distinguished Name)?
   - What port should we use?
   - Do we need SSL/TLS?

2. **Test Credentials:**
   - Can we have a test employee ID and password to verify connectivity?

### Step 3: Create .env File

Copy the template:
```bash
cp .env.template .env
```

Edit `.env` and update these critical values:

```env
# Enable LDAP
LDAP_ENABLED=True

# LDAP Configuration (REPLACE WITH REAL VALUES FROM IT)
LDAP_DOMAIN=UNIVERSAL              # Your Windows domain
LDAP_HOST=ad-server.halykbank.kz   # Your AD server
LDAP_PORT=389                      # Standard LDAP port
LDAP_BASE_DN=OU=Employees,DC=halykbank,DC=kz  # Your OU path

# Security (if required by IT)
LDAP_USE_SSL=False  # Set to True if using LDAPS (port 636)
LDAP_USE_TLS=False  # Set to True if using STARTTLS

# Whitelist (REPLACE WITH REAL EMPLOYEE IDs)
PERMITTED_USERS=00058215:Nadir:hr:read,write,admin;00037099:Saltanat:hr:read,write,admin;00060673:Meirim:manager:read,write

# JWT Secret (GENERATE NEW ONE!)
JWT_SECRET_KEY=your-generated-secret-key-here
```

### Step 4: Generate Strong JWT Secret

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and paste it into `.env` as `JWT_SECRET_KEY`.

### Step 5: Test LDAP Connectivity

Create a test script `test_ldap_connection.py`:

```python
#!/usr/bin/env python3
"""
Test LDAP connectivity before activating the system
"""
import sys
sys.path.append('.')

from ldap import check_ldap_password

# Replace with real test credentials from IT
TEST_EMPLOYEE_ID = "00058215"  # Replace with your employee ID
TEST_PASSWORD = "your-test-password"  # Replace with test password

print("🔍 Testing LDAP connection...")
print(f"📋 Employee ID: {TEST_EMPLOYEE_ID}")
print(f"🔐 Password: {'*' * len(TEST_PASSWORD)}")
print()

try:
    result = check_ldap_password(TEST_EMPLOYEE_ID, TEST_PASSWORD)

    if result:
        print("✅ SUCCESS! LDAP authentication working correctly")
        print("   You can now activate LDAP in your .env file")
    else:
        print("❌ FAILED: Authentication failed")
        print("   Possible reasons:")
        print("   - Incorrect employee ID or password")
        print("   - Employee not in Active Directory")
        print("   - LDAP server unreachable")
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("   Possible reasons:")
    print("   - LDAP server hostname is incorrect")
    print("   - Port is blocked by firewall")
    print("   - Domain name is incorrect")

print()
print("💡 Check login_history.log for detailed error messages")
```

Run the test:
```bash
python test_ldap_connection.py
```

Expected output if successful:
```
✅ SUCCESS! LDAP authentication working correctly
```

### Step 6: Check Logs

Review the LDAP authentication log:
```bash
tail -f login_history.log
```

You should see entries like:
```
2025-11-10 14:30:00:INFO:Loaded 3 permitted users from environment
2025-11-10 14:30:05:INFO:Attempting to bind with user DN: UNIVERSAL\00058215
2025-11-10 14:30:06:INFO:Successfully authenticated user: 00058215
2025-11-10 14:30:06:INFO:Successful login for user 00058215 (Nadir) at 2025-11-10 14:30:06
```

### Step 7: Start the Application

```bash
python main.py
```

Look for this message:
```
✅ LDAP authentication module loaded successfully
```

### Step 8: Test Login

1. Navigate to: `http://your-server:8000/login`
2. Enter your employee ID and AD password
3. Click "Войти в систему"
4. You should be redirected to the appropriate dashboard based on your role

---

## 🔍 Troubleshooting

### Issue: "LDAP authentication is not configured"

**Cause**: LDAP module failed to load or `LDAP_ENABLED=False`

**Solution**:
1. Check that ldap3 is installed: `pip list | grep ldap3`
2. Verify `.env` file exists and has `LDAP_ENABLED=True`
3. Restart the application

### Issue: "Доступ к ресурсу отсутствует" (Access denied)

**Cause**: Employee ID not in whitelist

**Solution**:
1. Add employee ID to `PERMITTED_USERS` in `.env`
2. Format: `EMPLOYEE_ID:NAME:ROLE:PERMISSIONS`
3. Restart the application

### Issue: "The username or password you have entered is incorrect"

**Cause**: LDAP authentication failed

**Possible reasons**:
1. Wrong employee ID or password
2. Employee not in Active Directory
3. LDAP server unreachable
4. Incorrect domain name or Base DN

**Solution**:
1. Verify credentials with IT department
2. Check `login_history.log` for detailed errors
3. Test connectivity with `test_ldap_connection.py`

### Issue: Connection timeout or "LDAP authentication error"

**Cause**: Cannot reach LDAP server

**Solution**:
1. Verify LDAP_HOST is correct
2. Check firewall rules (port 389 or 636 must be open)
3. Test from application server: `ping ldap-server.company.local`
4. Contact IT department to verify network connectivity

---

## 📊 System Architecture

### Authentication Flow

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ 1. Enter employee_id + password
       ↓
┌─────────────────┐
│  /api/login     │
└────────┬────────┘
         │ 2. Verify whitelist
         ↓
┌───────────────────────┐
│  LDAP Authentication  │──→ Active Directory
└────────┬──────────────┘
         │ 3. Validate credentials
         ↓
┌─────────────────┐
│  HR Database    │
└────────┬────────┘
         │ 4. Create/update user
         ↓
┌─────────────────┐
│  Generate JWT   │
└────────┬────────┘
         │ 5. Return token
         ↓
┌─────────────────┐
│    Dashboard    │
└─────────────────┘
```

### Database Integration

- **Employee ID stored in**: `users.phone` field (temporary mapping)
- **User auto-creation**: On first successful LDAP login
- **User updates**: Name and role synced from LDAP on each login

---

## 🔒 Security Features

### Two-Layer Authentication

1. **Whitelist Check**: Employee must be in `PERMITTED_USERS`
2. **AD Verification**: Password verified against Active Directory

### Audit Logging

All authentication attempts logged to `login_history.log`:
- Successful logins
- Failed attempts (wrong password)
- Access denials (not whitelisted)
- Errors (connection issues)

### JWT Token Security

- 8-hour expiration (configurable)
- HS256 algorithm
- Signed with JWT_SECRET_KEY

---

## 📝 Configuration Reference

### LDAP Settings

| Variable | Description | Example |
|----------|-------------|---------|
| `LDAP_ENABLED` | Enable/disable LDAP | `True` |
| `LDAP_DOMAIN` | Windows domain | `UNIVERSAL` |
| `LDAP_HOST` | LDAP server address | `ad.company.com` |
| `LDAP_PORT` | LDAP port | `389` (LDAP) or `636` (LDAPS) |
| `LDAP_BASE_DN` | Base Distinguished Name | `OU=Employees,DC=company,DC=com` |
| `LDAP_USE_SSL` | Use SSL | `True` or `False` |
| `LDAP_USE_TLS` | Use STARTTLS | `True` or `False` |
| `LDAP_TIMEOUT` | Connection timeout (seconds) | `10` |

### Whitelist Format

```
EMPLOYEE_ID:NAME:ROLE:PERMISSIONS;EMPLOYEE_ID:NAME:ROLE:PERMISSIONS
```

**Roles**:
- `hr` - Full access (view all results, manage system)
- `manager` - Department access (view/rate department employees)
- `employee` - Self access only (take tests, view own results)

**Permissions** (comma-separated, no spaces):
- `read` - View data
- `write` - Create/update data
- `admin` - Administrative functions

**Example**:
```env
PERMITTED_USERS=00058215:Nadir:hr:read,write,admin;00037099:Saltanat:hr:read,write,admin;00060673:Meirim:manager:read,write
```

---

## 🆘 Getting Help

### Check Documentation

1. This file (`LDAP_SETUP.md`)
2. `.env.template` - Configuration template with comments
3. `login_history.log` - Authentication logs

### Contact Support

- **IT Department**: LDAP server configuration issues
- **HR Department**: Whitelist management
- **Development Team**: Application bugs or feature requests

### Useful Commands

```bash
# View recent login attempts
tail -n 50 login_history.log

# Test LDAP connectivity
python test_ldap_connection.py

# Check if LDAP module is loaded
python -c "from ldap import authenticate_user; print('✅ LDAP module OK')"

# View current configuration
python -c "import config; print(f'LDAP Enabled: {config.LDAP_ENABLED}')"

# Generate new JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 📋 Maintenance

### Adding New Users

1. Add employee ID to `PERMITTED_USERS` in `.env`
2. Restart application
3. User will be auto-created on first login

### Removing Users

1. Remove employee ID from `PERMITTED_USERS` in `.env`
2. Restart application
3. User can no longer login (existing data preserved in database)

### Updating User Roles

1. Edit employee's role in `PERMITTED_USERS` in `.env`
2. Restart application
3. Role will be synced on next login

### Log Rotation

The `login_history.log` file grows indefinitely. Consider implementing log rotation:

```python
# In ldap.py, replace logging.basicConfig with:
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'login_history.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5
)
logging.getLogger().addHandler(handler)
```

---

## ✅ Activation Checklist

Before going to production:

- [ ] LDAP server details obtained from IT
- [ ] Test credentials verified
- [ ] `.env` file created from `.env.template`
- [ ] All placeholder values replaced with real data
- [ ] `LDAP_ENABLED=True` set
- [ ] Strong JWT secret generated
- [ ] Whitelist populated with real employee IDs
- [ ] LDAP connectivity tested successfully
- [ ] Test login performed
- [ ] Logs reviewed for errors
- [ ] Backup of database taken
- [ ] Old registration endpoint confirmed deprecated
- [ ] Users notified of new login process

---

## 🎉 Success Criteria

You've successfully activated LDAP when:

✅ Application starts with "✅ LDAP authentication module loaded successfully"
✅ Login page shows "✅ LDAP активирован" status
✅ Employees can login with their AD credentials
✅ Unauthorized employees get "Доступ к ресурсу отсутствует"
✅ Wrong passwords get "The username or password you have entered is incorrect"
✅ `login_history.log` shows successful authentication
✅ Users are auto-created in database on first login
✅ Role-based redirects work correctly

---

**Last Updated**: 2025-11-10
**Version**: 1.0
**Author**: Development Team
