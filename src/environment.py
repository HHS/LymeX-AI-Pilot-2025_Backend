from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(BaseSettings):
    frontend_url: str = Field("http://localhost:3000")
    application_name: str = Field("NOIS2-192")

    is_production: bool = Field(False)

    mongo_uri: str
    mongo_db: str

    access_token_secret: str
    access_token_expiration_seconds: int

    refresh_token_secret: str
    refresh_token_expiration_seconds: int

    forgot_password_token_secret: str
    forgot_password_token_expiration_seconds: int

    verify_email_token_secret: str
    verify_email_token_expiration_seconds: int

    rabbitmq_url: str
    mongo_celery_backend: str

    smtp_host: str
    smtp_port: str
    smtp_username: str
    smtp_password: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


environment = Environment()
