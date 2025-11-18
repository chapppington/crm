from pydantic import (
    computed_field,
    Field,
)
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Config(BaseSettings):
    postgres_db: str = Field(
        default="organization_catalog",
        alias="POSTGRES_DB",
    )

    postgres_user: str = Field(
        default="postgres",
        alias="POSTGRES_USER",
    )

    postgres_password: str = Field(
        default="postgres",
        alias="POSTGRES_PASSWORD",
    )

    postgres_port: int = Field(
        default=5432,
        alias="POSTGRES_PORT",
    )

    postgres_host: str = Field(
        default="localhost",
        alias="POSTGRES_HOST",
    )

    jwt_secret_key: str = Field(
        alias="JWT_SECRET_KEY",
        default="secret-key",
    )

    @computed_field
    @property
    def postgres_connection_uri(self) -> str:
        """Build PostgreSQL connection URI from components to build SQLAlchemy
        engine."""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
