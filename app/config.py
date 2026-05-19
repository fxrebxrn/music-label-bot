from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    bot_token: str
    database_url: str

    label_name: str
    label_link: str

    faq_link_royalty: str
    faq_link_privacy: str
    faq_link_terms: str

    debug: bool

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
