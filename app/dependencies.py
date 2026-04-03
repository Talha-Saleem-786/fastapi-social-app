from typing import Annotated
from sqlalchemy.orm import Session
from .database import get_db
from fastapi import Depends

DB = Annotated[Session, Depends(get_db)]