from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.core.config import settings
from app.core.logging import logger
import traceback

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Password hashing

def verify_password(plain_password, hashed_password):
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        logger.debug(f"Password verification: {'success' if result else 'failed'}")
        return result
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def get_password_hash(password):
    try:
        hashed = pwd_context.hash(password)
        logger.debug("Password hashed successfully")
        return hashed
    except Exception as e:
        logger.error(f"Password hashing error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

# JWT token creation

def create_access_token(data: dict, expires_delta: timedelta = None):
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        username = data.get("sub", "unknown")
        logger.info(f"Access token created for user: {username}, expires: {expire}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Access token creation error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def create_refresh_token(data: dict):
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        username = data.get("sub", "unknown")
        logger.info(f"Refresh token created for user: {username}, expires: {expire}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Refresh token creation error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_type = payload.get("type", "unknown")
        username = payload.get("sub", "unknown")
        logger.debug(f"Token decoded successfully: type={token_type}, user={username}")
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Token decode error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None 