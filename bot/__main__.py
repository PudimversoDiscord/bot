from asyncio import run

import discord
import sqlalchemy
import sqlalchemy.ext.asyncio
from discord.ext import commands
from bot.constants import Bot
from bot.bot import Pudimversify
from bot.data.database import engine
from bot.data import orm


async def setup_database() -> None:
    async with engine.begin() as conn:
        try:
            await conn.run_sync(orm.Base.metadata.create_all)
        except sqlalchemy.exc.SQLAlchemyError as e:
            raise RuntimeError(f"Não foi possível criar as tabelas: {e}") from e


def setup_logging():
    discord.utils.setup_logging(level=Bot.logger_level)


async def main():
    setup_logging()
    await setup_database()
    bot = Pudimversify(
        command_prefix=commands.when_mentioned_or(Bot.prefix),
        intents=discord.Intents.all(),
    )
    async with bot:
        try:
            await bot.start(Bot.token)
        except Exception as e:
            bot.logger.error(f"Error starting the bot: {e}")


if __name__ == "__main__":
    run(main())
