# pdx/__main__.py
from asyncio import run

import discord
from discord.ext import commands

from pdx.constants import Bot
from pdx.core import Utopiafy


def setup_logging():
    discord.utils.setup_logging(level=Bot.logger_level)


async def main():
    setup_logging()
    bot = Utopiafy(
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
