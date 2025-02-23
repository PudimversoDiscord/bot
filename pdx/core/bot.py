import logging
from contextlib import asynccontextmanager

from discord.ext import commands
from pdx.data.database import get_session


class Utopiafy(commands.Bot):
    """Utopiafy II"""

    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            *args,
            **kwargs,
        )
        self.logger = logging.getLogger("discord")

    @asynccontextmanager
    async def get_session(self):
        async with get_session() as session:
            yield session

    async def setup_hook(self) -> None:
        extensions = [
            "pdx.ext.cogs.fun.commands",
        ]
        for extension in extensions:
            self.logger.log(
                level=logging.INFO,
                msg=f"Carregando extensão: {extension}",
            )
            await self.load_extension(extension)
        return await super().setup_hook()
