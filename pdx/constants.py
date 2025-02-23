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


Guild = _Guild()


class _GuildCategories(
    EnvConfig,
    env_prefix="GUILD_CATEGORIES_",
):
    """Configurações das categorias do servidor."""

    staff: int = 1216042190006911119
    """ID da categoria de staff."""
    community: int = 1216042192389275771
    """ID da categoria de comunidade."""


GuildCategories = _GuildCategories()


class _GuildChannels(
    EnvConfig,
    env_prefix="GUILD_CHANNELS_",
):
    """Configurações dos canais do servidor."""

    welcome: int = 1216042190199980053
    """ID do canal de boas-vindas."""
    rules: int = 1216042190199980061
    """ID do canal de regras."""
    announcements: int = 1216047976561246219
    """ID do canal de anúncios."""


GuildChannels = _GuildChannels()


class _GuildRoles(
    EnvConfig,
    env_prefix="GUILD_ROLES_",
):
    """Configurações dos cargos do servidor."""

    admins: int = 1216042189193351215
    """ID do cargo de administradores."""
    mods: int = 1216042189193351212
    """ID do cargo de moderadores."""


GuildRoles = _GuildRoles()

# Shorthands
MODERATION_ROLES = [GuildRoles.admins, GuildRoles.mods]
