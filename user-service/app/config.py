
from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    database_url:str
    algorithm:str
    secret_key:str
    access_token_expire_minutes:int
    class Config():
        env_file=".env"
setting=Settings()