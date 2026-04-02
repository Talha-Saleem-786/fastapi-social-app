from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings
import os
from loguru import logger
# 1. Try to get the full URL first (Railway's default)
DATABASE_URL = os.getenv("MYSQL_URL")

if DATABASE_URL:
    # Handle the driver prefix for SQLAlchemy
    if DATABASE_URL.startswith("mysql://"):
        SQLALCHEMY_DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+mysqlconnector://", 1)
    else:
        SQLALCHEMY_DATABASE_URL = DATABASE_URL
    logger.info("Using production database URL")
else:
    # 2. Local development fallback
    port = settings.database_port if settings.database_port else "3306"
    SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{port}/{settings.database_name}"
    logger.info("Using local database configuration")
# 3. Create the engine]
try:
  engine = create_engine(
      SQLALCHEMY_DATABASE_URL,
      echo=True,
      pool_pre_ping=True
  )
except Exception:
    logger.critical("Database connection failed")
    raise

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        logger.debug("DB session started")
        yield db
    except Exception as e:
        logger.exception("Database session error")
        raise
    finally:
        db.close()
        logger.debug("DB session closed")