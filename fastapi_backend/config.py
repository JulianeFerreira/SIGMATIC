from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Sistema de Controle de Compras GAA"
    APP_DESCRIPTION: str = (
        "Sistema para gerenciamento de processos de compras, "
        "licitações e contratos da Polícia Científica do Paraná"
    )
    APP_VERSION: str = "1.0"

    # Banco de dados (pode trocar depois por PostgreSQL)
    DATABASE_URL: str = "sqlite:///./compras_gaa.db"

    # Configurações de email (placeholders)
    SMTP_ENABLED: bool = True
    SMTP_HOST: str = "smtp.exemplo.pr.gov.br"
    SMTP_PORT: int = 587
    SMTP_USER: str = "usuario"
    SMTP_PASSWORD: str = "senha"

    # Configuração de leitura de .env no Pydantic v2
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",  # ignora variáveis extras
    )


settings = Settings()
