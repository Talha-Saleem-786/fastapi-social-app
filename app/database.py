# from sqlalchemy import create_engine
from fastapi import HTTPException
from sqlalchemy.orm import  declarative_base
from .config import settings
import os
from loguru import logger
import sentry_sdk
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
# 1. Try to get the full URL first (Railway's default)
DATABASE_URL = os.getenv("MYSQL_URL")

if DATABASE_URL:
    # Handle the driver prefix for SQLAlchemy
    if DATABASE_URL.startswith("mysql://"):
        SQLALCHEMY_DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+aiomysql://", 1)
    else:
        SQLALCHEMY_DATABASE_URL = DATABASE_URL
    logger.info("Using production database URL")
else:
    # 2. Local development fallback
    port = settings.database_port if settings.database_port else "3306"
    SQLALCHEMY_DATABASE_URL = f"mysql+aiomysql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{port}/{settings.database_name}"
    logger.info("Using local database configuration")

try:
  engine = create_async_engine(
      SQLALCHEMY_DATABASE_URL,
      echo=True,
      pool_pre_ping=True
  )
  logger.success("Database engine created successfully")
except Exception as e:
    logger.critical("Database connection failed")
    sentry_sdk.capture_exception(e)
    raise

AsyncSessionLocal  = async_sessionmaker(
    engine,
    class_=AsyncSession,    # ✅ AsyncSession use karo
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    # db = AsyncSessionLocal()
    async with AsyncSessionLocal() as db:
      try:
          logger.debug("DB session started")
          yield db
      except HTTPException:
        raise
      except Exception as e:
          logger.error(f"Database session error | error={e}")
          sentry_sdk.capture_exception(e)
          raise
      finally:
        #   db.close()  #async with khud close karta hai — alag se nahi likhna!
          logger.debug("DB session closed")