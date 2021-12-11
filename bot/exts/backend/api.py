import logging

from discord.ext import commands

from bot.bot import Bot

log = logging.getLogger(__name__)


class API(commands.Cog):
    """Fetches data from the backed API."""

    def __init__(self, bot: Bot):
        self.bot = bot

    # @tasks.loop(seconds=30)
    # async def fetch_clients(self):
    #     """Fetch the connected clients."""
    #     with self.bot.http_session.get(f"{settings.api_url}/clients") as resp:
    #         print(resp)


def setup(bot: Bot) -> None:
    """Loads the API cog."""
    bot.add_cog(API(bot))
