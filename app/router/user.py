from fastapi import HTTPException, status, Depends, APIRouter
from .. import models, schemas
from sqlalchemy.orm import Session
from ..database import get_db   
from ..utils import hash_password
from loguru import logger
import sentry_sdk
router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreated, db: Session = Depends(get_db)):
    logger.info(f"User Registeration Attempt | email:{user.email}")
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        logger.warning(f"User {user.email} already exist!")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Email already registered")
    try:
      new_user = models.User(email=user.email, password=hash_password(user.password))
      db.add(new_user)
      db.commit()
      db.refresh(new_user)
      logger.success(f"User successfully created | email:{user.email} with id:{new_user.id}")
      return new_user
    except Exception as e:
        logger.error(f"User creation failed | email={user.email} | error={e}")
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User created failed")


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching User | id:{id}")
    try:
      user = db.query(models.User).filter(models.User.id == id).first()
      if not user:
          logger.warning(f"User {id} not found")
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"User with id {id} not found")
      logger.success(f"User succesfully Fetched | user:{user.id}")
      return user
    except HTTPException:
       raise
    except Exception as e:
       logger.error(f"Failed to fetch user | id={id} | error={e}")
       sentry_sdk.capture_exception(e)
       raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User fetched failed")
