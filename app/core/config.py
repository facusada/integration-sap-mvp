from functools import lru_cache

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="dev", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    sap_rfc_mock_mode: bool = Field(default=True, validation_alias="SAP_RFC_MOCK_MODE")
    sap_ashost: str = Field(default="", validation_alias=AliasChoices("SAP_RFC_ASHOST", "SAP_ASHOST"))
    sap_sysnr: str = Field(default="", validation_alias=AliasChoices("SAP_RFC_SYSNR", "SAP_SYSNR"))
    sap_client: str = Field(default="", validation_alias=AliasChoices("SAP_RFC_CLIENT", "SAP_CLIENT"))
    sap_user: str = Field(default="", validation_alias=AliasChoices("SAP_RFC_USER", "SAP_USER"))
    sap_password: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("SAP_RFC_PASSWD", "SAP_PASSWORD"),
    )
    sap_lang: str = Field(default="EN", validation_alias=AliasChoices("SAP_RFC_LANG", "SAP_LANG"))
    sap_default_system_id: str = Field(default="DEV", alias="SAP_DEFAULT_SYSTEM_ID")

    def sap_connection_params(self) -> dict[str, str]:
        password = self.sap_password.get_secret_value() if self.sap_password else ""
        return {
            "ashost": self.sap_ashost,
            "sysnr": self.sap_sysnr,
            "client": self.sap_client,
            "user": self.sap_user,
            "passwd": password,
            "lang": self.sap_lang,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
