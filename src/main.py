"""Main application entry point.

Initializes the FastAPI application, configures CORS, registers global
exception handlers, and includes the master router for all domain APIs.
Also manages the database schema creation on startup.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import AsyncGenerator

from src.conf import settings
from src.database.engine import async_engine, Base
from src.core.exceptions import AppException
from src.modules import api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application lifecycle events.

    On startup: Connects to the database and creates all tables if
    they don't already exist.
    On shutdown: Closes the database engine.
    """
    async with async_engine.begin() as conn:
        # For MVP, create all tables. In production, use Alembic.
        await conn.run_sync(Base.metadata.create_all)
    
    yield

    await async_engine.dispose()


app = FastAPI(
    title="Team Managemnt Platform API",
    version="1.0.0",
    description="Backend API for the team management platform.",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Hardcoded fallback because CORS_ORIGINS is not in settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Global handler for all domain-specific application exceptions.

    Converts any ``AppException`` subclass into a standardized JSON response
    containing the error code and message.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallback handler for uncaught server errors.

    Prevents leaking internal stack traces to the client in production.
    """
    # In a real app, log the stack trace here.
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected server error occurred.",
        },
    )


# Include the master API router
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    # Allows starting the server directly via `python src/main.py`
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
    )
