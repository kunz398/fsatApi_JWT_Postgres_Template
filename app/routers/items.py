from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.item import ItemCreate, ItemResponse
from app.models.item import Item
from app.models.user import User
from app.core.database import AsyncSessionLocal
from app.core.security import decode_access_token
from app.core.logging import logger, log_exceptions
from fastapi.security import OAuth2PasswordBearer
from typing import List
from sqlalchemy import select
import traceback

router = APIRouter(prefix="/api/items", tags=["items"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_access_token(token)
        if not payload or payload.get("type") != "access":
            logger.warning("Authentication failed: Invalid access token")
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        result = await db.execute(select(User).where(User.username == payload["sub"]))
        user = result.scalars().first()
        
        if not user:
            logger.warning(f"Authentication failed: User not found for username: {payload['sub']}")
            raise HTTPException(status_code=401, detail="User not found")
        
        logger.debug(f"User authenticated: {user.username} (ID: {user.id})")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=401, detail="Authentication failed")

@router.post("/", response_model=ItemResponse)
@log_exceptions
async def create_item(item: ItemCreate, request: Request, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    logger.info(f"Item creation attempt by user: {current_user.username} (ID: {current_user.id})")
    logger.info(f"Item details: title='{item.title}', description='{item.description}'")
    
    try:
        db_item = Item(**item.dict(), owner_id=current_user.id)
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
        
        logger.info(f"Item created successfully: ID={db_item.id}, title='{db_item.title}', owner={current_user.username}")
        return db_item
        
    except Exception as e:
        logger.error(f"Item creation error for user {current_user.username}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to create item")

@router.get("/", response_model=List[ItemResponse])
@log_exceptions
async def read_items(request: Request = None, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    logger.info(f"Items list request by user: {current_user.username} (ID: {current_user.id})")
    
    try:
        # Show all items without any limit
        result = await db.execute(select(Item))
        items = result.scalars().all()
        
        logger.info(f"Items retrieved successfully for user {current_user.username}: {len(items)} items")
        return items
        
    except Exception as e:
        logger.error(f"Items list error for user {current_user.username}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to retrieve items")

@router.get("/{item_id}", response_model=ItemResponse)
@log_exceptions
async def read_item(item_id: int, request: Request, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    logger.info(f"Item detail request by user: {current_user.username} (ID: {current_user.id}) for item ID: {item_id}")
    
    try:
        result = await db.execute(select(Item).where(Item.id == item_id, Item.owner_id == current_user.id))
        item = result.scalars().first()
        
        if not item:
            logger.warning(f"Item not found: ID={item_id}, requested by user={current_user.username}")
            raise HTTPException(status_code=404, detail="Item not found")
        
        logger.info(f"Item retrieved successfully: ID={item.id}, title='{item.title}', owner={current_user.username}")
        return item
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Item detail error for user {current_user.username}, item {item_id}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to retrieve item")

@router.delete("/{item_id}")
@log_exceptions
async def delete_item(item_id: int, request: Request, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    logger.info(f"Item deletion request by user: {current_user.username} (ID: {current_user.id}) for item ID: {item_id}")
    
    try:
        result = await db.execute(select(Item).where(Item.id == item_id, Item.owner_id == current_user.id))
        item = result.scalars().first()
        
        if not item:
            logger.warning(f"Item not found for deletion: ID={item_id}, requested by user={current_user.username}")
            raise HTTPException(status_code=404, detail="Item not found")
        
        await db.delete(item)
        await db.commit()
        
        logger.info(f"Item deleted successfully: ID={item.id}, title='{item.title}', owner={current_user.username}")
        return {"msg": "Item deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Item deletion error for user {current_user.username}, item {item_id}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to delete item") 