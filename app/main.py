from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, items
from app.core.database import engine, Base, database
from app.models.user import User
from app.models.item import Item
from app.core.logging import logger, log_exceptions
import time
import traceback

app = FastAPI(title="FastAPI JWT Template", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
        
        return response
    except Exception as e:
        # Log error
        process_time = time.time() - start_time
        logger.error(f"Request failed: {request.method} {request.url} - {str(e)} - {process_time:.4f}s")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler: {str(exc)}")
    logger.error(f"Request: {request.method} {request.url}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.on_event("startup")
@log_exceptions
async def startup():
    logger.info("Starting FastAPI application...")
    try:
        await database.connect()
        logger.info("Database connected successfully")
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified successfully")
        
        logger.info("FastAPI application started successfully")
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

@app.on_event("shutdown")
@log_exceptions
async def shutdown():
    logger.info("Shutting down FastAPI application...")
    try:
        await database.disconnect()
        logger.info("Database disconnected successfully")
        logger.info("FastAPI application shut down successfully")
    except Exception as e:
        logger.error(f"Shutdown error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

# Routers
app.include_router(auth)
app.include_router(items)

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"msg": "FastAPI JWT Template is running!"}

@app.get("/health")
async def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "healthy", "timestamp": time.time()} 