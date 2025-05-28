from pydantic import Field
from pydantic_settings import BaseSettings
from loguru import logger


class Environment(BaseSettings):
    base_url: str = Field("http://localhost:8000")
    refresh_token: str


environment = Environment()

print("Environment variables loaded successfully.")
logger.info("Environment variables loaded successfully.")
print(f"Base URL: {environment.base_url}")
print(f"Refresh token: {environment.refresh_token}")
