from pydantic_settings import BaseSettings


class EnvConfig(
    BaseSettings,
    env_file=(".env.server", ".env"),
    env_file_encoding="utf-8",
    env_nested_delimiter="__",
    extra="ignore",
):
    """Modelo de configurações que serão preenchidos pelo `.env`."""


class _Bot(
    EnvConfig,
    env_prefix="BOT_",
):
    """Configurações do bot."""

    token: str = ""
    """Token do bot."""
    prefix: str = "$"
    """Prefixo do bot."""
    logger_level: str = "INFO"
    """Nível de log do bot."""


Bot = _Bot()


class _Database(
    EnvConfig,
    env_prefix="DATABASE_",
):
    """Configurações do banco de dados."""

    url: str = "postgresql+asyncpg://bot:bot@localhost:5432/pudimverso"
    """URL de conexão com o banco de dados."""
    pool: int = 10
    """Tamanho do pool de conexões."""


Database = _Database()
