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
    url: str = "postgresql+asyncpg://pdx:pdx@localhost:5432/pudimverso"
    """URL de conexão com o banco de dados."""
    pool: int = 10
    """Tamanho do pool de conexões."""


Database = _Database()


class _Guild(
    EnvConfig,
    env_prefix="GUILD_",
):
    """Configurações do servidor."""
    id: int = 1216042188996083774
    """ID do servidor."""
    categories: dict[str, int] = {
        "INFORMAÇÃO": 1216042190199980059,
        "MODERAÇÃO": 0,  # FIXME: Adicionar ID da categoria de moderação
        "EVENTOS": 1216042191781232722,
        "COMUNIDADE": 1216042192389275771,
        "ENTRETENIMENTO": 1216042192884338803,
        "VOZ": 1233467914510925924,
    }

    """IDs das categorias do servidor."""


class _GuildChannels(
    EnvConfig,
    env_prefix="GUILD_CHANNELS_",
):
    """Configurações dos canais do servidor."""
    announcements: int = 0
    """ID do canal de anúncios."""


GuildChannels = _GuildChannels()


class _GuildRoles(
    EnvConfig,
    env_prefix="GUILD_ROLES_",
):
    """Configurações dos cargos do servidor."""

    admin: int = 1216042189193351213
    """ID do cargo de administrador."""
    mod: int = 1216042189193351212
    """ID do cargo de moderador."""
    bots: int = 1232037568963678258
    """ID do cargo de bots."""


GuildRoles = _GuildRoles()

# Atalhos
MODERATION_ROLES = [GuildRoles.admin, GuildRoles.mod]
"""Lista de cargos de moderação."""
