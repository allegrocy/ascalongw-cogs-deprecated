from .info import Info
from redbot.core.bot import Red
from discord.ext import commands

def setup(bot: Red):
    bot.add_cog(Info(bot))
