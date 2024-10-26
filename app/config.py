import os
from dotenv import load_dotenv
from pydantic import BaseModel, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV = os.path.join(os.path.dirname(__file__), ".env")

load_dotenv(DOTENV)


class EvenlabsSettings(BaseSettings):
    KEY: str

    model_config = SettingsConfigDict(env_prefix="EVENLABS_")


class DatabaseSettings(BaseSettings):
    ENGINE: str
    PATH: str

    @computed_field
    @property
    def database_url(self) -> str:
        return f"{self.ENGINE}:///{self.PATH}"

    model_config = SettingsConfigDict(env_prefix="SQLITE_DATABASE_")


class GreenAPI(BaseSettings):
    phonenumber: str
    access_token: str
    ID_INSTANCE: str
    TOKEN_INSTANCE: str
    URL: str
    model_config = SettingsConfigDict(env_prefix="GREEN_API_")


class OpenAISettings(BaseSettings):
    KEY: str
    timeout: int
    URL: str
    PROMPT: str
    model_config = SettingsConfigDict(env_prefix="OPENAI_")


class OtherSettings(BaseSettings):
    FIRST_MESSAGE: str

    model_config = SettingsConfigDict(env_prefix="OTHER_")


class Settings(BaseModel):
    OTHER: OtherSettings = OtherSettings()
    DATABASE: DatabaseSettings = DatabaseSettings()
    GPT: OpenAISettings = OpenAISettings()
    VOICE: EvenlabsSettings = EvenlabsSettings()
    CHAT: GreenAPI = GreenAPI()


settings = Settings()
