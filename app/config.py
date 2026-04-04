from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, Annotated


class Setting(BaseSettings):
    database_hostname: Optional[Annotated[str, Field(
        min_length=1,
        description="Database hostname"
    )]] = None

    database_port: Optional[Annotated[str, Field(
        pattern=r'^\d+$',       
        description="Database port"
    )]] = None


    database_password: Optional[Annotated[str, Field(
        min_length=1,
        description="Database password"
    )]] = None

    database_name: Optional[Annotated[str, Field(
        min_length=1,
        description="Database name"
    )]] = None

    database_username: Optional[Annotated[str, Field(
        min_length=1,
        description="Database username"
    )]] = None

    secret_key: Annotated[str, Field(
        min_length=32,        
        description="JWT secret key"
    )]


    algorithm: Annotated[str, Field(
        pattern=r'^(HS256|HS384|HS512|RS256)$',  
        description="JWT algorithm"
    )]

    access_token_expire_minutes: Annotated[int, Field(
        gt=0,
        le=10080,               
        description="Token expiry in minutes"
    )]
    class Config:
        env_file = ".env"
settings = Setting()