import logging
from collections import namedtuple
from typing import Iterable

import arrow
from aiohttp import ClientConnectorError
from discord import Embed, Option
from discord.commands import (ApplicationContext, AutocompleteContext,
                              slash_command)
from discord.ext import commands

from bot import settings
from bot.bot import Bot
from bot.core import constants

log = logging.getLogger(__name__)

Session = namedtuple("Session", ["host", "port"])


class Client(commands.Cog):
    """Manage and select connected clients."""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.sessions = []

        # Required to limit the API requests.
        self.last_fetched = arrow.Arrow(1, 1, 1)

    async def session_picker(self, ctx: AutocompleteContext) -> Iterable[str]:
        """Return a list of all connected clients."""
        # Only fetch the clients if 10 seconds has passed from the last fetch.
        if (arrow.utcnow() - self.last_fetched).seconds > 10:
            try:
                async with self.bot.http_session.get(f"{settings.api_url}/clients") as resp:
                    if resp.ok:
                        self.sessions = await resp.json()
            except ClientConnectorError:
                log.error("Could not fetch the clients, maybe the API is not running?")

            self.last_fetched = arrow.utcnow()

        return [f"{session['host']}:{session['port']}" for session in self.sessions if
                f"{session['host']}:{session['port']}".startswith(ctx.value)]

    @slash_command(guild_ids=settings.guild_ids)
    async def connect(self, ctx: ApplicationContext,
                      client: Option(str, autocomplete=session_picker, description="The client's host:port.")) -> None:
        """Connect to a specific session."""
        host, port = client.split(":")
        self.bot.connected_client = Session(host, int(port))

        embed = Embed(
            colour=constants.colours.bright_green,
            description=f"Session switched to **{host}:{port}** {constants.emojis.smiling_imp}"
        )
        await ctx.respond(embed=embed)

    @slash_command(guild_ids=settings.guild_ids)
    async def session(self, ctx: ApplicationContext) -> None:
        """Show the current connected session."""
        client = self.bot.connected_client
        if client:
            embed = Embed(
                colour=constants.colours.bright_green,
                description=f"Currently connected to **{client.host}:{client.port}**."
            )
        else:
            embed = Embed(
                colour=constants.colours.red,
                description=":x: Not connected to any session, run **/connect** first."
            )

        await ctx.respond(embed=embed)


def setup(bot: Bot) -> None:
    """Loads the Session cog."""
    bot.add_cog(Client(bot))
