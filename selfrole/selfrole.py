import discord
from redbot.core import checks
from discord.ext import commands
import os
import json

path = os.path.dirname(os.path.abspath(__file__))
data_dir = path + "/data"

class RoleError(Exception):
    pass
    
class Selfrole:
    """Self role!"""

    def __init__(self, bot):
        self.bot = bot
        try:
            with open(data_dir + "/role_data.json", "r") as f:
                self.role_data = json.loads(f.read())
        except:
            self.role_data = {}


    async def add_or_remove_role(self, message, role_name):
        try:
            channel = message.channel
            user = message.author
            guild = message.guild
            role_to_change = None
            for role in guild.roles:
                if role.name.lower() == role_name:
                    role_to_change = role

            if role_to_change is None:
                raise RoleError("The role **{}** cannot be found. Please create one.".format(role_name))

            already_roled = False

            for user_role in user.roles:
                if role_name.lower() == user_role.name.lower():
                    already_roled = True

            try:
                if already_roled is True:
                    await user.remove_roles(role_to_change)
                    await channel.send("\N{OK HAND SIGN} I have removed you from **{}**.".format(role_to_change.name))
                elif already_roled is False:
                    await user.add_roles(role_to_change)
                    await channel.send("\N{OK HAND SIGN} I have added you to **{}**.".format(role_to_change.name))
            except discord.errors.Forbidden:
                if not (channel.permissions_for(ctx.me).manage_roles or channel.permissions_for(ctx.me).administrator):
                    err = "I don't have permission to manage roles."
                else:
                    err = ('a role I tried to assign or remove is too high '
                           'for me to do so.')
                raise RoleError('Error updating roles: ' + err)
        except Exception as e:
            await ctx.send(e)

    @checks.is_owner()
    @commands.command()
    async def addsr(self, ctx, role_name):
        """Add a role to the selfrole-able list."""
        try:
            guild = ctx.guild
            role_name = role_name.lower()
            role_to_change = None
            for role in guild.roles:
                if role.name.lower() == role_name:
                    role_to_change = role
                    break
            
            if role_to_change is None:
                raise RoleError("The role **{}** cannot be found. Please create one.".format(role_name))

            guild_id = str(guild.id)
            if self.role_data.get(guild_id) is None:
                self.role_data[guild_id] = []
            if role_to_change.name.lower() not in self.role_data[guild_id]:
                if len(self.role_data[guild_id]) == 0:
                    self.role_data[guild_id] = []
                self.role_data[guild_id].append(role_name)

                await ctx.send("Added **{}** to your server's selfrole list. Users may now register themselves with the command **-{}**.".format(role_to_change.name, role_name))
            else:
                self.role_data[guild_id].remove(role_name)
                await ctx.send("Removed **{}** from your server's selfrole list. Users may no longer register themselves with the command **-{}**.".format(role_to_change.name, role_name))
            with open(data_dir + "/role_data.json", "w") as f:
                json.dump(self.role_data, f)
        except RoleError as e:
            await ctx.send(e)

    async def selfrole_monitor(self, message):
        guild = message.guild
        if guild is not None and message.author.id != self.bot.user.id and message.content[0] == "-":
            role_name = message.content[1:].lower()
            guild_id = str(guild.id)
            if role_name in self.role_data[guild_id]:
                await self.add_or_remove_role(message, role_name)
            else:
                pass

    @checks.is_owner()
    @commands.command()
    async def reset_role_data(self, ctx, role_name):
        """Reset the selfrole-able list."""
        self.role_data = {}

    @checks.is_owner()
    @commands.command()
    async def debug_role_data(self, ctx):
        """Load, read and print role_data"""
        with open(data_dir + "/role_data.json", "r") as f:
            self.role_data = json.loads(f.read())
            print(self.role_data)