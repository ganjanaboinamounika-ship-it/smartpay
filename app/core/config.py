from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "SmartPay"
    APP_VERSION: str = "1.0.0"

    ENVIRONMENT: str = "development"

    DATABASE_URL: str
    REDIS_URL: str
    RABBITMQ_URL: str

    JWT_SECRET: str
    JWT_ALGORITHM: Literal["HS256"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, gt=0, le=1440)

    WEBHOOK_SECRET: str
    WEBHOOK_ENCRYPTION_KEY: str

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, value):
        value = value.strip().lower()

        if value not in {"development", "testing", "production"}:
            raise ValueError(
                "ENVIRONMENT must be development, testing, or production"
            )

        return value

    @model_validator(mode="after")
    def validate_production_secrets(self):
        if self.ENVIRONMENT == "production":
            if len(self.JWT_SECRET) < 32:
                raise ValueError("Production JWT_SECRET must be at least 32 characters")

            if len(self.WEBHOOK_SECRET) < 32:
                raise ValueError("Production WEBHOOK_SECRET must be at least 32 characters")

            placeholders = {
                "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET",
                "CHANGE_THIS_WEBHOOK_SECRET",
                "CHANGE_THIS_SECRET",
            }

            if self.JWT_SECRET in placeholders or self.WEBHOOK_SECRET in placeholders:
                raise ValueError("Production secrets cannot use example placeholders")

        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()