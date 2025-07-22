from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from loguru import logger


class Environment(BaseSettings):
    # APPLICATION CONFIGURATION
    application_name: str = Field("NOIS2-192")
    application_description: str = Field("NOIS2-192 API")
    application_version: str = Field("0.1.0")
    application_host: str = Field("http://localhost:8000")
    frontend_url: str = Field("http://localhost:3000")

    ai_service_url: str = Field("http://localhost:19003")

    system_admin_password: str = Field("admin1234!@#@WEd23ewd")

    is_production: bool = Field(False)

    # DATABASE CONFIGURATION

    mongo_uri: str
    mongo_db: str

    # JWT CONFIGURATION

    access_token_secret: str
    access_token_expiration_seconds: int

    totp_login_token_secret: str
    totp_login_token_expiration_seconds: int

    verify_login_token_secret: str
    verify_login_token_expiration_seconds: int
    verify_login_token_number_of_digits: int

    refresh_token_secret: str
    refresh_token_expiration_seconds: int

    forgot_password_token_secret: str
    forgot_password_token_expiration_seconds: int

    verify_email_token_secret: str
    verify_email_token_expiration_seconds: int

    # TOTP
    totp_digits: int = Field(6)
    totp_interval: int = Field(30)
    totp_valid_window: int = Field(1)

    # CELERY CONFIGURATION

    rabbitmq_url: str
    mongo_celery_backend: str

    # EMAIL CONFIGURATION

    smtp_host: str
    smtp_port: str
    smtp_username: str
    smtp_password: str

    # MINIO CONFIGURATION
    minio_internal_endpoint: str
    minio_root_user: str
    minio_root_password: str
    minio_bucket: str

    redis_host: str
    redis_port: str = Field(6379)
    redis_db: str = Field(0)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


environment = Environment()

logger.info("Environment variables loaded successfully.")
logger.debug(environment.model_dump_json(indent=4))
