from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Government Job Automation Platform API"
    API_V1_STR: str = "/api/v1"
    
    # SECURITY
    SECRET_KEY: str = "super_secret_enterprise_key_change_in_production_1234567890"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 # 8 days
    
    # DATABASE
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = "job_recruitment_ai" # Assuming the user's current db is job_recruitment_ai

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
