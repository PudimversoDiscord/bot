import logging
from discord.ext import commands


class Pudimversify(commands.Bot):
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

    async def setup_hook(self) -> None:
        return await super().setup_hook()
