# 🧪 LDAP Authentication Testing Guide

## Overview

This guide provides multiple ways to test the LDAP authentication system depending on your current setup and requirements.

---

## Testing Options

### ✅ Option 1: Mock Mode Testing (RECOMMENDED FOR NOW)

**When to use**: Testing without access to real LDAP/Active Directory server

**What it tests**:
- ✅ Login UI and user experience
- ✅ Authentication flow logic
- ✅ Whitelist validation
- ✅ Token generation and storage
- ✅ Role-based redirects
- ✅ Error handling
- ❌ Does NOT test actual LDAP connection

#### Method A: Command-Line Mock Test

Test the authentication module directly:

```bash
python test_ldap_mock.py
```

**Expected Output**:
```
==================================================================
🧪 MOCK LDAP TESTING MODE
==================================================================

LDAP authentication has been mocked for testing.
Any employee_id in the whitelist with password 'test123' will work.

Whitelist (from ldap.py):
  - PLACEHOLDER_EMPLOYEE_ID_1 (role: hr)
  - PLACEHOLDER_EMPLOYEE_ID_2 (role: manager)
  - PLACEHOLDER_EMPLOYEE_ID_3 (role: employee)

Test 1: Valid credentials
✅ Success: {'employee_id': 'PLACEHOLDER_EMPLOYEE_ID_1', 'name': 'Test User 1', ...}

Test 2: Invalid password
❌ Expected failure: The username or password you have entered is incorrect.

Test 3: User not in whitelist
❌ Expected failure: Доступ к ресурсу отсутствует
```

#### Method B: Full Application Mock Test

Start the FastAPI server with mock LDAP:

```bash
python run_with_mock.py
```

**Test Credentials**:
- **Employee ID**: `PLACEHOLDER_EMPLOYEE_ID_1` (HR role)
- **Password**: `test123`

**OR**

- **Employee ID**: `PLACEHOLDER_EMPLOYEE_ID_2` (Manager role)
- **Password**: `test123`

**OR**

- **Employee ID**: `PLACEHOLDER_EMPLOYEE_ID_3` (Employee role)
- **Password**: `test123`

**Test Steps**:
1. Navigate to: `http://localhost:8000/login`
2. Enter any placeholder employee_id from above
3. Enter password: `test123`
4. Click "Войти в систему"
5. You should be redirected based on role:
   - HR → `/hr/menu`
   - Manager → `/manager/menu`
   - Employee → `/specializations`

**What to verify**:
- ✅ Login page loads correctly with Halyk branding
- ✅ LDAP status shows "⚠️ LDAP не активирован"
- ✅ Valid credentials log you in successfully
- ✅ Invalid password shows error: "The username or password you have entered is incorrect"
- ✅ Non-whitelisted employee_id shows: "Доступ к ресурсу отсутствует"
- ✅ Token is saved in sessionStorage
- ✅ Redirect works based on role
- ✅ Check `login_history.log` for authentication records

---

### 🔧 Option 2: UI Testing (No Backend Required)

**When to use**: Testing only the login page design and frontend behavior

**What it tests**:
- ✅ Login page UI/UX
- ✅ Form validation
- ✅ Loading states
- ✅ Error message display
- ❌ Does NOT test authentication logic

**Steps**:
1. Open `templates/login.html` directly in browser
2. Try entering various inputs
3. Check responsive design on mobile/tablet
4. Verify placeholder text and labels are correct

---

### 🏢 Option 3: Real LDAP Testing (Requires IT Department)

**When to use**: Final testing before production deployment

**What it tests**:
- ✅ Real Active Directory connection
- ✅ Actual employee credentials
- ✅ Network connectivity
- ✅ Firewall rules
- ✅ SSL/TLS configuration
- ✅ Production readiness

**Prerequisites**:
1. LDAP server details from IT department
2. Test employee credentials
3. Network access to LDAP server (port 389 or 636)

**Steps**:

#### Step 1: Create `.env` file

```bash
cp .env.template .env
```

Edit `.env` with real values from IT:

```env
# Enable LDAP
LDAP_ENABLED=True

# Real LDAP Configuration (from IT department)
LDAP_DOMAIN=UNIVERSAL
LDAP_HOST=ad-server.halykbank.kz  # Real server from IT
LDAP_PORT=389
LDAP_BASE_DN=OU=Employees,DC=halykbank,DC=kz  # Real DN from IT

# Real Whitelist (from HR department)
PERMITTED_USERS=00058215:Nadir:hr:read,write,admin;00037099:Saltanat:hr:read,write,admin

# Generate new JWT secret
JWT_SECRET_KEY=<run: python -c "import secrets; print(secrets.token_urlsafe(32))">
```

#### Step 2: Test LDAP connectivity

Create test script `test_real_ldap.py`:

```python
#!/usr/bin/env python3
"""Test real LDAP connection"""
import sys
sys.path.append('.')

from ldap import check_ldap_password

# Replace with real test credentials from IT
TEST_EMPLOYEE_ID = "00058215"  # Real employee ID
TEST_PASSWORD = "your-real-password"  # Real AD password

print("🔍 Testing REAL LDAP connection...")
print(f"📋 Employee ID: {TEST_EMPLOYEE_ID}")
print()

try:
    result = check_ldap_password(TEST_EMPLOYEE_ID, TEST_PASSWORD)

    if result:
        print("✅ SUCCESS! LDAP authentication working")
    else:
        print("❌ FAILED: Authentication failed")
        print("   Check: employee ID, password, or AD account status")
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("   Check: LDAP server, port, domain name, network connectivity")

print()
print("💡 Check login_history.log for detailed error messages")
```

Run:
```bash
python test_real_ldap.py
```

#### Step 3: Start application

```bash
python main.py
```

**Look for**:
```
✅ LDAP authentication module loaded successfully
INFO:     Application startup complete.
```

#### Step 4: Test login

1. Navigate to: `http://localhost:8000/login`
2. Enter real employee ID and AD password
3. Check LDAP status shows "✅ LDAP активирован"
4. Verify successful login

---

## Testing Checklist

### 📋 Mock Mode Testing

- [ ] Command-line mock test runs successfully (`python test_ldap_mock.py`)
- [ ] Valid credentials accepted
- [ ] Invalid password rejected with correct error
- [ ] Non-whitelisted employee_id rejected
- [ ] Web server starts with mock mode (`python run_with_mock.py`)
- [ ] Login page loads at `/login`
- [ ] Mock authentication works via UI
- [ ] Role-based redirects work (HR → `/hr/menu`, etc.)
- [ ] Token saved in sessionStorage
- [ ] `login_history.log` records authentication attempts

### 📋 UI Testing

- [ ] Login page renders correctly
- [ ] Halyk Bank branding displays
- [ ] Form validation works (required fields)
- [ ] Loading spinner shows during submission
- [ ] Error messages display correctly
- [ ] Responsive design works on mobile
- [ ] LDAP status indicator shows correctly

### 📋 Real LDAP Testing (when ready)

- [ ] LDAP server details obtained from IT
- [ ] `.env` file created with real values
- [ ] `LDAP_ENABLED=True` set
- [ ] Strong JWT secret generated
- [ ] Whitelist populated with real employee IDs
- [ ] Connectivity test passes (`test_real_ldap.py`)
- [ ] Application starts without errors
- [ ] Login page shows "✅ LDAP активирован"
- [ ] Real employee can login with AD password
- [ ] Unauthorized employee gets access denied
- [ ] Wrong password shows error message
- [ ] `login_history.log` shows successful authentication
- [ ] User auto-created in database on first login
- [ ] Role synced from whitelist correctly

---

## Common Testing Scenarios

### Scenario 1: Valid Login (Mock Mode)

**Test**: Login with whitelisted employee
```
Employee ID: PLACEHOLDER_EMPLOYEE_ID_1
Password: test123
```

**Expected Result**:
- ✅ Authentication successful
- ✅ Redirected to `/hr/menu`
- ✅ Token saved in sessionStorage
- ✅ Log entry in `login_history.log`

### Scenario 2: Invalid Password

**Test**: Wrong password
```
Employee ID: PLACEHOLDER_EMPLOYEE_ID_1
Password: wrongpassword
```

**Expected Result**:
- ❌ Error: "The username or password you have entered is incorrect."
- ❌ Stays on login page
- ✅ Log entry showing failed attempt

### Scenario 3: Not Whitelisted

**Test**: Employee not in permitted users
```
Employee ID: INVALID_EMPLOYEE_ID
Password: test123
```

**Expected Result**:
- ❌ Error: "Доступ к ресурсу отсутствует"
- ❌ Stays on login page
- ✅ Log entry showing access denied

### Scenario 4: Empty Fields

**Test**: Submit without credentials
```
Employee ID: (empty)
Password: (empty)
```

**Expected Result**:
- ❌ Browser validation prevents submission
- ❌ Required field messages shown

### Scenario 5: Role-Based Access

**Test**: Login as different roles
```
# Test as HR
Employee ID: PLACEHOLDER_EMPLOYEE_ID_1
Expected redirect: /hr/menu

# Test as Manager
Employee ID: PLACEHOLDER_EMPLOYEE_ID_2
Expected redirect: /manager/menu

# Test as Employee
Employee ID: PLACEHOLDER_EMPLOYEE_ID_3
Expected redirect: /specializations
```

---

## Debugging Tips

### Issue: "LDAP authentication is not configured"

**Cause**: LDAP module failed to load

**Fix**:
```bash
# Install ldap3
pip install ldap3

# Verify installation
python -c "import ldap3; print('✅ ldap3 OK')"

# Check if module loads
python -c "from ldap import authenticate_user; print('✅ LDAP module OK')"
```

### Issue: Mock mode not working

**Cause**: Real LDAP being called instead of mock

**Fix**:
1. Ensure you're using `run_with_mock.py` NOT `main.py`
2. Check console for "🧪 MOCK LDAP MODE ACTIVATED" message
3. Verify mock is patching before module import

### Issue: Login page shows "LDAP не активирован"

**Explanation**: This is CORRECT for placeholder mode
- When `LDAP_ENABLED=False` (default), you'll see this warning
- This is intentional - system knows it's using placeholders
- Once you set `LDAP_ENABLED=True` with real config, it will show "✅ LDAP активирован"

### Issue: Can't connect to real LDAP server

**Checklist**:
1. Verify LDAP_HOST is correct: `ping ldap-server.company.local`
2. Check port is open: `nc -zv ldap-server.company.local 389`
3. Verify domain name with IT
4. Check firewall rules
5. Review `login_history.log` for detailed errors

---

## Next Steps

### For Development (Now):
1. ✅ Run mock mode testing with `python run_with_mock.py`
2. ✅ Test all authentication scenarios
3. ✅ Verify UI/UX works as expected
4. ✅ Check error handling

### For Production (Later):
1. ⏳ Coordinate with IT department for LDAP details
2. ⏳ Get whitelist from HR department
3. ⏳ Create `.env` file with real values
4. ⏳ Run connectivity tests
5. ⏳ Deploy and monitor `login_history.log`

---

## Support Resources

- **LDAP Setup Guide**: See `LDAP_SETUP.md` for detailed activation steps
- **Configuration Template**: See `.env.template` for all available settings
- **Mock Testing**: Use `test_ldap_mock.py` or `run_with_mock.py`
- **Logs**: Check `login_history.log` for authentication audit trail

---

**Last Updated**: 2025-11-10
**Author**: Development Team
