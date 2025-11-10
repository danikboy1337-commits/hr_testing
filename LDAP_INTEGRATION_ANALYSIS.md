# 🔐 LDAP Authentication Integration Analysis

## Executive Summary

Your colleague has provided an **Active Directory (LDAP) authentication script** to restrict access to company employees only. This document analyzes the LDAP implementation and provides detailed integration strategies for your HR testing platform.

---

## 📋 Part 1: LDAP File Analysis

### Overview

**File:** `ldap.py` (220 lines)
**Purpose:** Authenticate users against company Active Directory and restrict access to whitelisted employees
**Technology:** LDAP3 library with NTLM authentication

### Key Components

#### 1. **LDAP Configuration** (Lines 24-32)

```python
LDAP_CONFIG = {
    'domain': 'UNIVERSAL',
    'host': 'xxxxxxxxx',            # Your AD server
    'port': 389,                    # Standard LDAP port
    'base_dn': 'OU=xxx,DC=xxx,...', # Organizational Unit
    'use_ssl': False,
    'use_tls': False,
    'timeout': 10,
}
```

**Analysis:**
- ✅ Uses Windows domain authentication (NTLM)
- ✅ Connects to internal Active Directory server
- ⚠️ SSL/TLS disabled (acceptable if internal network)
- ✅ Configurable via environment variables
- ✅ Timeout protection (10 seconds)

#### 2. **Whitelist System** (Lines 34-96)

```python
PERMITTED_USERS = {
    '00058215': {'name': 'Nadir', 'role': 'admin', 'permissions': [...]},
    '00037099': {'name': 'Saltanat', 'role': 'admin', 'permissions': [...]},
    '00060673': {'name': 'Meirim', 'role': 'admin', 'permissions': [...]},
}
```

**Analysis:**
- ✅ Uses employee IDs as keys (e.g., '00058215')
- ✅ Supports environment variable configuration
- ✅ Format: `USER_ID:NAME:ROLE:PERMISSIONS`
- ✅ Example: `00058215:Nadir:admin:read,write,admin`
- ✅ Falls back to hardcoded defaults if env var not set
- ✅ Robust error handling for invalid formats

#### 3. **LDAP Authentication** (Lines 100-139)

```python
def check_ldap_password(username: str, password: str) -> bool:
    server = Server(LDAP_CONFIG['host'], ...)
    user_dn = f"{LDAP_CONFIG['domain']}\\{username}"
    conn = Connection(server, user=user_dn, password=password, authentication=NTLM)
    return conn.bind()
```

**Analysis:**
- ✅ Authenticates against Active Directory
- ✅ Uses NTLM (Windows authentication)
- ✅ User format: `DOMAIN\username` (e.g., `UNIVERSAL\00058215`)
- ✅ Logs all authentication attempts
- ✅ Proper exception handling
- ✅ Connection cleanup (unbind)

#### 4. **JWT Token Management** (Lines 141-162)

```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    expire = datetime.utcnow() + timedelta(minutes=480)  # 8 hours
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

**Analysis:**
- ✅ JWT tokens for session management
- ✅ 8-hour expiration (480 minutes)
- ✅ Uses HS256 algorithm
- ✅ Secret key from environment variable
- ⚠️ Longer than current system (7 days)

#### 5. **Two-Step Authentication** (Lines 164-195)

```python
def authenticate_user(username: str, password: str):
    # Step 1: Check whitelist
    if username not in PERMITTED_USERS:
        raise HTTPException(403, "Access denied")

    # Step 2: Validate against LDAP
    if not check_ldap_password(username, password):
        raise HTTPException(401, "Incorrect credentials")

    return user_info
```

**Analysis:**
- ✅ **Double verification**: Whitelist + LDAP
- ✅ Different HTTP codes: 403 (not permitted) vs 401 (wrong password)
- ✅ Logging: tracks both failed and successful attempts
- ✅ Returns user data: username, name, role, permissions
- ✅ Secure: Even if someone has LDAP credentials, they must be whitelisted

#### 6. **Logging System** (Lines 12-16, throughout)

```python
logging.basicConfig(filename='login_history.log', level=logging.INFO)
logging.info(f"Successful login for user {username} at {now}")
logging.error(f"LDAP authentication error: {e}")
```

**Analysis:**
- ✅ All authentication attempts logged to file
- ✅ Timestamps for audit trail
- ✅ Distinguishes: success, failure, errors
- ✅ Useful for security monitoring

---

## 🔄 Part 2: Comparison with Current System

### Current HR Platform Authentication

| Feature | Current System | LDAP System |
|---------|---------------|-------------|
| **Authentication Method** | Phone-only (no password) | Username + Password (LDAP) |
| **User Identifier** | Phone number | Employee ID |
| **Verification** | Check if phone exists in DB | LDAP + Whitelist |
| **Registration** | Open (anyone can register) | Closed (whitelist only) |
| **Password** | None | LDAP/AD password |
| **Token Expiration** | 7 days | 8 hours |
| **Logging** | None | Comprehensive file logging |
| **Access Control** | None (anyone with phone) | Strict (whitelist + LDAP) |
| **Security Level** | Low (phone can be faked) | High (AD credentials required) |

### Key Differences

#### **Authentication Flow**

**Current System:**
```
User enters phone → Check DB → Generate token → Success
```

**LDAP System:**
```
User enters employee_id + password → Check whitelist → Verify LDAP → Generate token → Success
```

#### **User Registration**

**Current System:**
- ✅ Open registration
- ✅ Anyone can create account with phone
- ❌ No verification of company affiliation

**LDAP System:**
- ❌ No registration endpoint
- ✅ Only whitelisted employees allowed
- ✅ Verified against company AD

---

## 🎯 Part 3: Integration Strategies

### Option 1: **Full Replacement** (Recommended for Production)

**Description:** Replace current phone-based auth with LDAP completely

**Pros:**
- ✅ Maximum security
- ✅ Only company employees can access
- ✅ Uses existing AD infrastructure
- ✅ Centralized user management
- ✅ Audit trail via logging

**Cons:**
- ❌ More complex setup
- ❌ Requires LDAP server access
- ❌ External users cannot test

**Best For:**
- Production deployment
- Internal company use only
- When security is critical

---

### Option 2: **Hybrid System** (Recommended for Development)

**Description:** Support both phone-based and LDAP authentication

**Pros:**
- ✅ Flexibility for testing
- ✅ Gradual migration path
- ✅ External testers can still use phone
- ✅ Internal employees use LDAP

**Cons:**
- ❌ Two auth systems to maintain
- ❌ More complex code
- ❌ Potential security confusion

**Best For:**
- Development/Testing phase
- Gradual rollout
- Mixed audience (internal + external)

---

### Option 3: **Role-Based Selection** (Balanced Approach)

**Description:** Phone auth for employees, LDAP for HR/Managers only

**Pros:**
- ✅ Test takers use simple phone auth
- ✅ HR/Admin use secure LDAP auth
- ✅ Balanced security vs usability
- ✅ Protects sensitive functions

**Cons:**
- ❌ Complex role management
- ❌ Two different login flows

**Best For:**
- Mixed security requirements
- Public test-taking, secured admin panel
- Gradual security enhancement

---

## 📝 Part 4: Recommended Implementation (Hybrid Approach)

### Phase 1: Prepare Infrastructure

#### **Step 1: Install Dependencies**

Add to `requirements.txt`:
```
ldap3==2.9.1
```

Install:
```bash
pip install ldap3
```

#### **Step 2: Configure Environment**

Add to `.env`:
```env
# LDAP Configuration
LDAP_DOMAIN=UNIVERSAL
LDAP_HOST=xxxxxxxxx
LDAP_PORT=389
LDAP_BASE_DN=OU=xxx,DC=xxx,DC=xxx
LDAP_USE_SSL=False
LDAP_USE_TLS=False

# Permitted Users (semicolon-separated)
PERMITTED_USERS=00058215:Nadir:admin:read,write,admin;00037099:Saltanat:admin:read,write,admin;00060673:Meirim:admin:read,write,admin

# JWT Secret (must be strong in production)
SECRET_KEY=your-super-secret-key-change-in-production-123456
```

#### **Step 3: Update Config**

Add to `config.py`:
```python
# LDAP Settings
LDAP_DOMAIN = os.getenv("LDAP_DOMAIN", "UNIVERSAL")
LDAP_HOST = os.getenv("LDAP_HOST", "")
LDAP_PORT = int(os.getenv("LDAP_PORT", 389))
LDAP_BASE_DN = os.getenv("LDAP_BASE_DN", "")
LDAP_USE_SSL = os.getenv("LDAP_USE_SSL", "False").lower() == "true"
LDAP_USE_TLS = os.getenv("LDAP_USE_TLS", "False").lower() == "true"

# Permitted Users
PERMITTED_USERS_ENV = os.getenv("PERMITTED_USERS", "")
```

---

### Phase 2: Integrate LDAP Module

#### **Step 4: Update `ldap.py`**

Modify to use config values:
```python
# Replace hardcoded LDAP_CONFIG with:
import config

LDAP_CONFIG = {
    'domain': config.LDAP_DOMAIN,
    'host': config.LDAP_HOST,
    'port': config.LDAP_PORT,
    'base_dn': config.LDAP_BASE_DN,
    'use_ssl': config.LDAP_USE_SSL,
    'use_tls': config.LDAP_USE_TLS,
    'timeout': 10,
}
```

#### **Step 5: Add LDAP Login Endpoint**

Add to `main.py`:
```python
from ldap import authenticate_user as ldap_authenticate, create_access_token as ldap_create_token

class LDAPLoginRequest(BaseModel):
    employee_id: str
    password: str

@app.post("/api/ldap/login")
async def ldap_login(request: LDAPLoginRequest):
    """
    LDAP-based login for company employees
    Requires: employee_id (e.g., '00058215') and AD password
    """
    try:
        # Authenticate against LDAP + whitelist
        user_data = ldap_authenticate(request.employee_id, request.password)

        # Check if user exists in our database
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                # Try to find user by employee_id (stored in phone field)
                await cur.execute(
                    "SELECT id, name, surname, role, department_id FROM users WHERE phone = %s",
                    (request.employee_id,)
                )
                db_user = await cur.fetchone()

                if db_user:
                    # User exists in DB
                    user_id = db_user[0]
                else:
                    # Auto-create user from LDAP data
                    await cur.execute(
                        """INSERT INTO users (name, surname, phone, company, job_title, role)
                           VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
                        (
                            user_data['name'],
                            '',  # No surname from LDAP
                            request.employee_id,  # Store employee_id in phone field
                            'Halyk Bank',
                            user_data['role'],
                            user_data['role']  # admin/manager/employee
                        )
                    )
                    user_id = (await cur.fetchone())[0]

        # Create JWT token (using HR platform's token format)
        token = create_access_token(
            user_id=user_id,
            phone=request.employee_id,
            role=user_data['role'],
            department_id=None
        )

        return {
            "status": "success",
            "user_id": user_id,
            "name": user_data['name'],
            "employee_id": request.employee_id,
            "role": user_data['role'],
            "permissions": user_data['permissions'],
            "token": token,
            "auth_method": "ldap"
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### **Step 6: Create LDAP Login UI**

Create `/templates/ldap_login.html`:
```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Вход для сотрудников</title>
    <style>
        /* Similar styling to existing login.html */
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 40px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 8px;
        }
        button {
            width: 100%;
            padding: 14px;
            background: #1DB584;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h2>🔐 Вход для сотрудников</h2>
        <p>Используйте ваш корпоративный ID и пароль</p>

        <input id="employee_id" type="text" placeholder="Табельный номер (например, 00058215)" />
        <input id="password" type="password" placeholder="Пароль AD" />
        <button onclick="login()">Войти</button>

        <div id="error" style="color: red; margin-top: 10px;"></div>

        <p style="margin-top: 20px; text-align: center; font-size: 14px; color: #666;">
            <a href="/login">Вход по номеру телефона</a>
        </p>
    </div>

    <script>
        async function login() {
            const employee_id = document.getElementById('employee_id').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('/api/ldap/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({employee_id, password})
                });

                const data = await response.json();

                if (response.ok) {
                    localStorage.setItem('token', data.token);
                    localStorage.setItem('user_id', data.user_id);
                    localStorage.setItem('name', data.name);
                    localStorage.setItem('role', data.role);

                    // Redirect based on role
                    if (data.role === 'admin') {
                        window.location.href = '/hr-dashboard';
                    } else if (data.role === 'manager') {
                        window.location.href = '/manager-dashboard';
                    } else {
                        window.location.href = '/employee-dashboard';
                    }
                } else {
                    document.getElementById('error').innerText = data.detail || 'Ошибка входа';
                }
            } catch (error) {
                document.getElementById('error').innerText = 'Ошибка соединения с сервером';
            }
        }

        // Enter key support
        document.getElementById('password').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') login();
        });
    </script>
</body>
</html>
```

#### **Step 7: Add Route for LDAP Login Page**

Add to `main.py`:
```python
@app.get("/ldap-login", response_class=HTMLResponse)
async def ldap_login_page():
    with open("templates/ldap_login.html", "r", encoding="utf-8") as f:
        return f.read()
```

---

### Phase 3: Testing

#### **Step 8: Test LDAP Authentication**

1. **Start Application:**
   ```bash
   python main.py
   ```

2. **Navigate to LDAP Login:**
   ```
   http://localhost:8000/ldap-login
   ```

3. **Test with Whitelisted User:**
   - Employee ID: `00058215`
   - Password: (AD password)

4. **Expected Result:**
   - ✅ Success: Redirected to dashboard
   - ❌ Not in whitelist: "Access denied"
   - ❌ Wrong password: "Incorrect credentials"

5. **Check Logs:**
   ```bash
   tail -f login_history.log
   ```

---

## 🔒 Part 5: Security Considerations

### Strengths

| Feature | Security Level |
|---------|---------------|
| **Active Directory Integration** | ⭐⭐⭐⭐⭐ (Very High) |
| **Whitelist System** | ⭐⭐⭐⭐⭐ (Very High) |
| **Comprehensive Logging** | ⭐⭐⭐⭐⭐ (Very High) |
| **JWT Tokens** | ⭐⭐⭐⭐ (High) |
| **Two-Step Verification** | ⭐⭐⭐⭐⭐ (Very High) |

### Potential Issues

#### **1. SSL/TLS Disabled**
- ⚠️ **Issue:** Credentials sent in plaintext
- ✅ **Mitigation:** Acceptable if on internal network
- 💡 **Recommendation:** Enable TLS for production

#### **2. Hardcoded Defaults**
- ⚠️ **Issue:** Default users in code
- ✅ **Mitigation:** Override with environment variables
- 💡 **Recommendation:** Remove defaults in production

#### **3. Log File Access**
- ⚠️ **Issue:** `login_history.log` could grow large
- 💡 **Recommendation:** Implement log rotation
- 💡 **Recommendation:** Restrict file permissions (chmod 600)

#### **4. Secret Key**
- ⚠️ **Issue:** Weak default secret key
- ✅ **Mitigation:** Override with strong env variable
- 💡 **Recommendation:** Use cryptographically random string

### Recommended Security Enhancements

```python
# 1. Enable TLS for LDAP
LDAP_CONFIG['use_tls'] = True
LDAP_CONFIG['use_ssl'] = True

# 2. Add rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/api/ldap/login")
@limiter.limit("5/minute")  # Max 5 attempts per minute
async def ldap_login(...):
    ...

# 3. Add logging rotation
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler(
    'login_history.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5
)

# 4. Strong secret key (in .env)
import secrets
SECRET_KEY = secrets.token_urlsafe(32)  # Generate once, store in .env
```

---

## 📊 Part 6: Migration Strategy

### For Existing Users

**Problem:** Existing users have phone numbers, not employee IDs

**Solution 1: Data Mapping**
```sql
-- Add employee_id column
ALTER TABLE users ADD COLUMN employee_id VARCHAR(20);

-- Manual mapping (HR provides list)
UPDATE users SET employee_id = '00058215' WHERE phone = '+77001234567';
```

**Solution 2: Dual Authentication**
- Keep phone auth for existing users
- New users must use LDAP
- Gradual migration over time

---

## 🎯 Part 7: Recommended Next Steps

### Immediate Actions

1. ✅ **Review LDAP configuration** with IT department
   - Verify LDAP server address
   - Confirm domain name
   - Test connectivity

2. ✅ **Update whitelist** with actual employee IDs
   - Get list from HR
   - Format as environment variable
   - Test with 2-3 employees first

3. ✅ **Install dependencies**
   ```bash
   pip install ldap3
   ```

4. ✅ **Test in development**
   - Create test accounts
   - Verify LDAP connection
   - Check logging works

### Short-Term (1-2 weeks)

5. ✅ **Implement hybrid system**
   - Keep existing phone auth
   - Add LDAP login page
   - Test with pilot group

6. ✅ **Monitor and iterate**
   - Check login_history.log
   - Gather user feedback
   - Fix issues

### Long-Term (1-2 months)

7. ✅ **Full migration** (if successful)
   - Disable phone registration
   - Enforce LDAP for all
   - Remove old auth code

8. ✅ **Security hardening**
   - Enable TLS
   - Add rate limiting
   - Implement log rotation

---

## 📋 Part 8: Implementation Checklist

- [ ] Install `ldap3` package
- [ ] Update `.env` with LDAP configuration
- [ ] Test LDAP connectivity from server
- [ ] Update `ldap.py` with config integration
- [ ] Create `/api/ldap/login` endpoint
- [ ] Create `ldap_login.html` template
- [ ] Add route for LDAP login page
- [ ] Test with 1-2 employees
- [ ] Monitor `login_history.log`
- [ ] Add rate limiting (optional)
- [ ] Enable TLS (optional, for production)
- [ ] Document for IT team

---

## 💡 Part 9: Summary & Recommendation

### Analysis Summary

✅ **LDAP Script Quality:** Professional, well-structured, production-ready
✅ **Security Level:** High (AD + whitelist + logging)
✅ **Integration Complexity:** Medium (2-3 days work)
✅ **Maintenance:** Low (once configured)

### Recommended Approach

**For Your Use Case (Proctored Room Testing):**

I recommend **Option 1: Full Replacement** because:
1. ✅ You're testing in a controlled environment (proctored room)
2. ✅ Only company employees should access
3. ✅ LDAP provides centralized authentication
4. ✅ Whitelist ensures only permitted employees
5. ✅ Logging provides audit trail for compliance

**Implementation Timeline:**
- Week 1: Setup & testing with IT
- Week 2: Pilot with 5-10 employees
- Week 3: Full rollout

**Estimated Effort:** 2-3 days of development + 1 week of testing

---

## 📞 Questions to Discuss with IT Team

Before implementation, clarify:

1. ✅ LDAP server address accessible from application server?
2. ✅ Domain name correct (UNIVERSAL)?
3. ✅ Port 389 open in firewall?
4. ✅ Base DN correct for employee OU?
5. ✅ Should we enable TLS? (recommended)
6. ✅ Who maintains the whitelist? (HR or IT)
7. ✅ Where should logs be stored? (consider centralized logging)
8. ✅ Token expiration policy? (8 hours vs 7 days)

---

**Generated:** 2025-11-07
**LDAP File Version:** As provided by colleague
**Integration Complexity:** Medium
**Recommended Timeline:** 2-3 weeks
**Security Level:** High ⭐⭐⭐⭐⭐
