from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import  status, HTTPException,Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app import schemas,database,models
from .config import settings
from loguru import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.success(f"Token created Succesfully for user_id: {data.get('user_id')}")
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    logger.info("Verifying access token...")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")   
        if user_id is None:
            logger.warning("Token verification failed: user_id missing")
            raise credentials_exception
        token_data = schemas.TokenData(id=str(user_id))
        logger.success(f"Token verified successfully for user_id: {user_id}")

    except JWTError as e:
        logger.error(f"Token verification error: {str(e)}")
        raise credentials_exception
    return token_data

def get_current_user(token: str = Depends(oauth2_scheme), db:Session =Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token =verify_access_token(token , credentials_exception)
    user= db.query(models.User).filter(models.User.id ==token.id).first()
    if not user:
        logger.warning(f"User not found with id: {token.id}")
        raise credentials_exception
    
    logger.info(f"User retrieved successfully: {user.id}")
    return user
