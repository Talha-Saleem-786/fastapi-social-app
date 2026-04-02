from fastapi import HTTPException, status, Depends, APIRouter
from app import schemas
from .. import models,utils,oauth2
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from loguru import logger
import sentry_sdk

router = APIRouter(
    tags=["Authentication"]
)

@router.post("/login", response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm=Depends(), db: Session = Depends(get_db)):
    logger.info(f"Login attempt | user:{user_credentials.username}")

    try:
      user = db.query(models.User).filter( models.User.email == user_credentials.username).first()
      if not user:
          logger.warning(f"Login failed | email not found={user_credentials.username}")
          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid credentials")
      if not utils.verify(user_credentials.password, user.password):
          logger.warning(f"Login failed | wrong password | email={user_credentials.username}")
          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid credentials")
      access_token=oauth2.create_token( data = {"user_id": user.id})
      logger.success(f"Login successful | email={user_credentials.username} user_id={user.id}")
      return {
      "access_token": access_token,
      "token_type": "bearer"
      }
    except HTTPException:
        raise  
    except Exception as e:
        logger.error(f"Login error | email={user_credentials.username} | error={e}")
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Login failed")