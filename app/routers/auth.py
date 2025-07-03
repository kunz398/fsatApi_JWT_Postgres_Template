from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User
from app.core.database import AsyncSessionLocal
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_access_token
from app.core.config import settings
from app.core.logging import logger, log_exceptions
from jose import JWTError
from typing import Optional
from datetime import timedelta
from sqlalchemy import select
import traceback

router = APIRouter(prefix="/api/auth", tags=["auth"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/register", response_model=UserResponse)
@log_exceptions
async def register(user: UserCreate, request: Request, db: AsyncSession = Depends(get_db)):
    logger.info(f"Registration attempt for username: {user.username}, email: {user.email}")
    
    try:
        # Check if user already exists
        result = await db.execute(select(User).where((User.username == user.username) | (User.email == user.email)))
        db_user = result.scalars().first()
        
        if db_user:
            logger.warning(f"Registration failed: User already exists - username: {user.username}, email: {user.email}")
            raise HTTPException(status_code=400, detail="Username or email already registered")
        
        # Create new user
        hashed_password = get_password_hash(user.password)
        new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        logger.info(f"User registered successfully: {new_user.username} (ID: {new_user.id})")
        return new_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error for {user.username}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login")
@log_exceptions
async def login(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None, db: AsyncSession = Depends(get_db)):
    logger.info(f"Login attempt for username: {form_data.username}")
    
    try:
        result = await db.execute(select(User).where(User.username == form_data.username))
        user = result.scalars().first()
        
        if not user or not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Login failed: Invalid credentials for username: {form_data.username}")
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        
        # Generate tokens
        access_token = create_access_token(data={"sub": user.username})
        refresh_token = create_refresh_token(data={"sub": user.username})
        
        logger.info(f"User logged in successfully: {user.username} (ID: {user.id})")
        
        return {
            "access_token": access_token, 
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for {form_data.username}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Login failed")

@router.post("/refresh")
@log_exceptions
async def refresh_token(refresh_token: str, request: Request = None):
    logger.info("Token refresh attempt")
    
    try:
        payload = decode_access_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            logger.warning("Token refresh failed: Invalid refresh token")
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        username = payload.get("sub")
        if not username:
            logger.warning("Token refresh failed: Invalid token payload")
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        access_token = create_access_token(data={"sub": username})
        logger.info(f"Token refreshed successfully for user: {username}")
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Token refresh failed")

@router.post("/logout")
@log_exceptions
async def logout(request: Request = None):
    logger.info("Logout request received")
    return {"msg": "Logout successful (client should delete tokens)"} 