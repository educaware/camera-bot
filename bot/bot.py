import logging
import socket
from abc import ABC

from aiohttp import AsyncResolver, ClientSession, TCPConnector
from discord import Cog, Embed, HTTPException, Interaction
from discord.ext import commands

from bot import trace_config
from bot.core import constants, settings

log = logging.getLogger(__name__)


class Bot(commands.Bot, ABC):
    """Base bot class."""

    name = settings.client.name

    def __init__(self, **kwargs):
        """Initiate the client with slash commands."""
        super().__init__(**kwargs)
        self.connected_client = None

        log.debug("Starting the HTTP session")
        self.http_session = ClientSession(
            connector=TCPConnector(resolver=AsyncResolver(), family=socket.AF_INET),
            trace_configs=[trace_config]
        )

    async def on_ready(self) -> None:
        """Triggered when the bot is ready."""
        name = f"{self.user} (ID: {self.user.id})"

        devlog_msg = f"Connected {constants.emojis.partying_face}"
        self.loop.create_task(self.send_log(devlog_msg, colour=constants.colours.bright_green))

        log.info(f"Started bot as {name}")

    async def on_interaction(self, interaction: Interaction) -> None:
        """Log whenever a command is used."""
        arguments = [option['value'] for option in interaction.data.get("options", "")]
        command = f"{interaction.data['name']} {arguments if arguments else ''}".rstrip()
        if interaction.is_command():
            log.info(f"{interaction.user} used /{command} (ID: {interaction.user.id})")

        await super().on_interaction(interaction)
        log.debug(f"/{command} ended (ID: {interaction.user.id})")

    def add_cog(self, cog: Cog, *, override: bool = False) -> None:
        """Log whenever a cog is loaded."""
        super().add_cog(cog, override=override)
        log.debug(f"Cog loaded: {cog.qualified_name}")

    async def send_log(self, description: str = None, colour: int = None, embed: Embed = None) -> None:
        """Send an embed message to the devlog channel."""
        devlog = self.get_channel(settings.channels.devlog)

        if not devlog:
            log.debug(f"Fetching the devlog channel as it wasn't found in the cache "
                      f"(ID: {settings.channels.devlog})")
            try:
                devlog = await self.fetch_channel(settings.channels.devlog)
            except HTTPException:
                log.debug(f"Could not fetch the devlog channel so log message won't be sent "
                          f"(ID: {settings.channels.devlog})")
                return

        if not embed:
            embed = Embed(description=description)

        if colour:
            embed.colour = colour

        await devlog.send(embed=embed)

    async def close(self) -> None:
        """Triggered when the bot is closed."""
        await super().close()

        if self.http_session:
            log.debug("Closing the HTTP session")
            await self.http_session.close()
