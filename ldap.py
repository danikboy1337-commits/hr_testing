
import logging
import datetime
from typing import Optional, Dict, Any
from ldap3 import Server, Connection, ALL, NTLM, Tls
from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# Configure logging
logging.basicConfig(
    filename='login_history.log', 
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

# LDAP Configuration
LDAP_CONFIG = {
    'domain': 'UNIVERSAL',                      
    'host': 'xxxxxxxxx',            
    'port': 389,                            
    'base_dn': 'OU=xxxxxxxxx,DC=xxxxxxxxx,DC=xxxxxxxxx',      
    'use_ssl': False,                        
    'use_tls': False,                        
    'timeout': 10,                            
}

def parse_permitted_users():
    # Default permitted users (fallback)
    default_users = {
        '00058215': {
            'name': 'Nadir',
            'role': 'admin',
            'permissions': ['read', 'write', 'admin']
        },
        '00037099': {
            'name': 'Saltanat',
            'role': 'admin',
            'permissions': ['read', 'write', 'admin']
        },
        '00060673': {
            'name': 'Meirim',
            'role': 'admin',
            'permissions': ['read', 'write', 'admin']
        },
    }
    
    # Try to read from environment variable
    users_env = os.getenv('PERMITTED_USERS', '')
    
    if not users_env:
        logging.info("No PERMITTED_USERS environment variable found, using default users")
        return default_users
    
    try:
        permitted_users = {}
        user_entries = users_env.split(';')
        
        for entry in user_entries:
            if not entry.strip():
                continue
                
            parts = entry.strip().split(':')
            if len(parts) != 4:
                logging.warning(f"Invalid user entry format: {entry}. Expected format: USER_ID:NAME:ROLE:PERMISSIONS")
                continue
            
            user_id, name, role, permissions_str = parts
            permissions = [p.strip() for p in permissions_str.split(',') if p.strip()]
            
            permitted_users[user_id] = {
                'name': name,
                'role': role,
                'permissions': permissions
            }
        
        if permitted_users:
            logging.info(f"Loaded {len(permitted_users)} permitted users from environment variable")
            return permitted_users
        else:
            logging.warning("No valid users found in PERMITTED_USERS environment variable, using defaults")
            return default_users
            
    except Exception as e:
        logging.error(f"Error parsing PERMITTED_USERS environment variable: {e}")
        logging.info("Using default permitted users")
        return default_users

# Load permitted users from environment or use defaults
PERMITTED_USERS = parse_permitted_users()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def check_ldap_password(username: str, password: str) -> bool:
    """
    Authenticate user against LDAP server
    Adapted from original Streamlit code
    """
    try:
        server = Server(
            LDAP_CONFIG['host'],
            port=LDAP_CONFIG['port'],
            use_ssl=LDAP_CONFIG['use_ssl'],
            get_info=ALL
        )

        if LDAP_CONFIG['use_tls']:
            tls_configuration = Tls(validate=False)  # ssl.CERT_NONE equivalent
            server.tls = tls_configuration

        user_dn = f"{LDAP_CONFIG['domain']}\\{username}"
        
        logging.info(f"Attempting to bind with user DN: {user_dn}")

        conn = Connection(
            server,
            user=user_dn,
            password=password,
            authentication=NTLM,
           auto_bind=True
        )

        if conn.bind():
            logging.info(f"Successfully authenticated user: {username}")
            conn.unbind()
            return True
        else:
            logging.error(f"Failed to authenticate user: {username}")
            return False
            
    except Exception as e:
        logging.error(f"LDAP authentication error: {e}")
        return False

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token and return user data"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return payload
    except JWTError:
        return None

def authenticate_user(username: str, password: str) -> Dict[str, Any]:
    """
    Authenticate user and return user info
    """
    now = datetime.datetime.now()
    
    # Check if user is in permitted list
    if username not in PERMITTED_USERS:
        logging.info(f"Not approved user {username} at {now}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ к ресурсу отсутствует"
        )
    
    # Authenticate against LDAP
    if not check_ldap_password(username, password):
        logging.info(f"Incorrect login attempt for user {username} at {now}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The username or password you have entered is incorrect."
        )
    
    # Get user info
    user_info = PERMITTED_USERS[username]
    logging.info(f"Successful login for user {username} ({user_info['name']}) at {now}")
    
    return {
        "username": username,
        "name": user_info['name'],
        "role": user_info['role'],
        "permissions": user_info['permissions']
    }

def get_current_user(token: str) -> Dict[str, Any]:
    """Get current user from token"""
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = payload.get("sub")
    if username not in PERMITTED_USERS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized"
        )
    
    user_info = PERMITTED_USERS[username]
    return {
        "username": username,
        "name": user_info['name'],
        "role": user_info['role'],
        "permissions": user_info['permissions']
    }