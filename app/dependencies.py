from typing import Annotated
# from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db
from fastapi import Depends

DB = Annotated[AsyncSession, Depends(get_db)]
