import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Anthropic API
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# App Settings
APP_HOST = os.getenv("HOST", "0.0.0.0")
APP_PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Organization
ORG_NAME = "Халык банк"
ORG_LOGO = "/static/images/halyk_logo.png"
ORG_PRIMARY_COLOR = "#1DB584"

# Security
HR_PASSWORD = os.getenv("HR_PASSWORD", "159753")  # Default for backward compatibility
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "halyk-hr-forum-super-secret-key-change-in-production")

RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY", "")
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY", "")

# LDAP Configuration (Placeholders - Update in .env when ready to activate)
LDAP_ENABLED = os.getenv("LDAP_ENABLED", "False").lower() == "true"  # Set to True to activate LDAP
LDAP_DOMAIN = os.getenv("LDAP_DOMAIN", "PLACEHOLDER_DOMAIN")
LDAP_HOST = os.getenv("LDAP_HOST", "placeholder-ldap-server.local")
LDAP_PORT = int(os.getenv("LDAP_PORT", "389"))
LDAP_BASE_DN = os.getenv("LDAP_BASE_DN", "OU=PLACEHOLDER,DC=PLACEHOLDER,DC=local")
LDAP_USE_SSL = os.getenv("LDAP_USE_SSL", "False").lower() == "true"
LDAP_USE_TLS = os.getenv("LDAP_USE_TLS", "False").lower() == "true"
LDAP_TIMEOUT = int(os.getenv("LDAP_TIMEOUT", "10"))

# Permitted LDAP Users (Semicolon-separated: USER_ID:NAME:ROLE:PERMISSIONS)
# Example: 00058215:Nadir:admin:read,write,admin;00037099:Saltanat:admin:read,write,admin
PERMITTED_USERS_ENV = os.getenv("PERMITTED_USERS", "")

# Test Configuration
TEST_TIME_LIMIT_MINUTES = int(os.getenv("TEST_TIME_LIMIT_MINUTES", "40"))

# Weighted Score Formula Weights
TEST_WEIGHT = float(os.getenv("TEST_WEIGHT", "0.5"))
MANAGER_WEIGHT = float(os.getenv("MANAGER_WEIGHT", "0.4"))
SELF_WEIGHT = float(os.getenv("SELF_WEIGHT", "0.1"))