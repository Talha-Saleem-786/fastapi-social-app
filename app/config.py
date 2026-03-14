from pydantic_settings import BaseSettings
from typing import Optional
class Setting(BaseSettings):
    database_hostname:Optional[str]=None
    database_port: Optional[str]=None
    database_password: Optional[str]=None
    database_name:Optional[str]=None
    database_username:Optional[str]=None
    secret_key:str
    algorithm:str
    access_token_expire_minutes:int
    class Config:
        env_file=".env"

settings= Setting()