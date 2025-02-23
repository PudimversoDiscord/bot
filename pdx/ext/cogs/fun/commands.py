import discord
from discord.ext import commands
from pdx import constants
from pdx.core import Utopiafy
from pdx.ext.cogs.fun.components.logic import markov


class Fun(commands.Cog):
    def __init__(self, bot: Utopiafy) -> None:
        self.bot = bot

    @commands.Cog.listener(
        "on_message",
    )
    async def learn(
        self,
        message: discord.Message,
    ) -> None:
        """Passivamente escuta as mensagens e aprende com elas."""

        should_ignore = any(
            (
                message.channel.category_id == constants.GuildCategories.staff,
                message.author.bot,
                message.content.startswith(constants.Bot.prefix),
                message.content.startswith("```"),
                message.content.startswith("https://"),
                not message.content,
            )
        )

        if should_ignore:
            return

        async with self.bot.get_session() as session:
            await markov.process_message(message.content, session)


async def setup(bot: Utopiafy) -> None:
    await bot.add_cog(Fun(bot))
