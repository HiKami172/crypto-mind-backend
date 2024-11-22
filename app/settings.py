from datetime import timedelta
from pathlib import Path

from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent

env_file = BASE_DIR / '.env'


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, extra='ignore')

    url: str = Field(alias='POSTGRES_URI')
    url_prod_: str | None = Field(alias='POSTGRES_URI_PROD', default=None)

    @property
    def url_prod(self):
        return self.url_prod_ or self.url


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, extra='ignore')

    OPENAI_API_KEY: str
    MODEL: str

    MAX_RESPONSES: int
    TEMPERATURE: float
    MAX_TOKENS: int
    TOP_P: int
    FREQUENCY_PENALTY: int
    PRESENCE_PENALTY: int


class BinanceSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, extra='ignore')

    BINANCE_API_KEY: str | None
    BINANCE_API_SECRET: str | None


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, extra='ignore')

    algorithms: str = Field(alias='PASSWORD_HASHING_ALGORITHM')
    key: str = Field(alias='PASSWORD_SECRET_KEY')
    access_expire: int = Field(alias='ACCESS_TOKEN_EXPIRE_MINUTES')
    refresh_expire: int = Field(alias='REFRESH_TOKEN_EXPIRE_MINUTES')


class OAuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, extra='ignore')

    GOOGLE_CLIENT_ID: str | None
    GOOGLE_CLIENT_SECRET: str | None
    GOOGLE_REDIRECT_URI: str | None


class Settings(BaseSettings):
    BROKER_ANALYTICS: int
    DEBUG: bool
    LOGGING_LEVEL: str = Field(default='DEBUG')
    CACHING_ENABLED: bool
    ALLOWED_ORIGINS: str = Field()
    ALLOWED_METHODS: str
    ALLOWED_HEADERS: str

    @property
    def ALLOWED_ORIGINS_LIST(self) -> list[str]:  # noqa
        return self.ALLOWED_ORIGINS.split(', ')

    @property
    def ALLOWED_METHODS_LIST(self) -> list[str]:  # noqa
        return self.ALLOWED_METHODS.split(', ')

    @property
    def ALLOWED_HEADERS_LIST(self) -> list[str]:  # noqa
        return self.ALLOWED_HEADERS.split(', ')

    database: DBSettings = DBSettings()
    llm: LLMSettings = LLMSettings()
    auth: AuthSettings = AuthSettings()
    oauth: OAuthSettings = OAuthSettings()

    model_config = SettingsConfigDict(env_file=env_file, extra='ignore')


settings = Settings()

logger.add(
    sink=BASE_DIR / 'logs' / 'all' / 'logs.log',
    level=settings.LOGGING_LEVEL,
    enqueue=True,
    rotation=timedelta(days=1),
    retention=timedelta(days=7),
)
logger.add(
    sink=BASE_DIR / 'logs' / 'errors' / 'errors.log',
    level='ERROR',
    enqueue=True,
    backtrace=True,
    diagnose=settings.DEBUG,
    rotation=timedelta(days=1),
    retention=timedelta(days=7),
)

logger.info(f"SETTINGS: {settings}")

if __name__ == '__main__':
    logger.info('Settings: {settings}', settings=settings)
