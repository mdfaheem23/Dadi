from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    whatsapp_access_token: str
    whatsapp_phone_number_id: str
    whatsapp_business_account_id: str
    whatsapp_webhook_verify_token: str
    meta_api_version: str = "v21.0"

    host: str = "0.0.0.0"
    port: int = 8000

    @property
    def whatsapp_api_base_url(self) -> str:
        return f"https://graph.facebook.com/{self.meta_api_version}"

    @property
    def whatsapp_messages_url(self) -> str:
        return f"{self.whatsapp_api_base_url}/{self.whatsapp_phone_number_id}/messages"

    @property
    def whatsapp_media_url(self) -> str:
        return f"{self.whatsapp_api_base_url}/{self.whatsapp_phone_number_id}/media"


settings = Settings()
