import logging

from discord.ext import commands


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

    async def setup_hook(self) -> None:
        self.logger.log(
            level=logging.INFO,
            msg="Hook foi bem-sucedido; iniciando...",
        )
        return await super().setup_hook()
