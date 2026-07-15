from contextlib import asynccontextmanager

from fastapi import Depends, Body, FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException

from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.middleware.exception_handler import (
    app_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.models import models

from app.config.database import Base, engine, create_tables, close_db_connections

from app.constants.constant import ROOT_DIR
from app.config.settings import settings

from app.utils.exceptions import APPException
from app.web import web_router
from app.api import api_router

from typing import Annotated


# App lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting FastAPI Production Template...")
    if settings.environment == "development":
        await create_tables()  # Uncomment when database is set up
        # Seed default categories if none exist
        from app.config.database import AsyncSessionLocal
        from app.models.models import Category
        async with AsyncSessionLocal() as session:
            result = await session.scalars(select(Category))
            if not result.first():
                categories = [
                    Category(name="Backend", description="Server-side programming, databases, APIs, and microservices."),
                    Category(name="Frontend", description="User interfaces, web frameworks, responsive layouts, and animations."),
                    Category(name="Data Analytics", description="Data processing, statistics, visualization, and insights."),
                    Category(name="DevOps", description="Continuous Integration/Deployment, cloud platforms, Docker, and monitoring."),
                    Category(name="AI & Machine Learning", description="Neural networks, natural language processing, LLMs, and computer vision.")
                ]
                session.add_all(categories)
                await session.commit()
                print("✅ Seeded default categories")
    print(
        f"✅ Server running on {settings.host}:{settings.port} (Database disabled for demo)"
    )

    yield

    # Shutdown
    print("🔄 Shutting down server...")
    await close_db_connections()  # Uncomment when database is set up
    print("✅ Server shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="FastAPI Blog",
    description="A comprehensive, production-ready FastAPI Blog template for Blog management with authentication, categories, priorities, and analytics",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)


if settings.app_mode in ["full", "web"]:
    app.mount("/static", StaticFiles(directory=ROOT_DIR / "static"), name="static")
    app.mount("/media", StaticFiles(directory=ROOT_DIR / "media"), name="media")


app.include_router(router=web_router)
app.include_router(router=api_router)


# Exception handlers
app.add_exception_handler(APPException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)



