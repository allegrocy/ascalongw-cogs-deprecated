import discord
from redbot.core import checks
from discord.ext import commands
    
class Lgit:
    """Special commands for the LGiT Discord Server"""

    def __init__(self, bot):
        self.bot = bot

    def get_channel(self, server, channel_name):
        return discord.utils.get(server.channels, name=channel_name)

    async def role_main(self, ctx, role_name):
        guild = ctx.guild
        channel = ctx.channel
        user = ctx.author
        role = discord.utils.get(guild.roles, name=role_name)
        already_roled = False

        for role_check in user.roles:
            if role_name == role_check.name:
                already_roled = True

        if already_roled is True and role_name != "Discord Member":
            await user.remove_roles(role)
        elif already_roled is False:
            await user.add_roles(role)

        return already_roled

    async def role_add(self, ctx, role_name):
        guild = ctx.guild
        channel = ctx.channel
        user = ctx.author
        role = discord.utils.get(guild.roles, name=role_name)
        already_roled = False

        for role_check in user.roles:
            if role_name == role_check.name:
                already_roled = True

        if already_roled is True:
            pass
        elif already_roled is False:
            await user.add_roles(role)

        return already_roled

    async def kurz_role(self, ctx):
        server = ctx.message.server
        channel = ctx.message.channel
        user = ctx.message.author
        role = discord.utils.get(server.roles, name="Kurzick")

        if "Luxon" in user.roles:
            await user.remove_roles(role)
            await ctx.send(ctx.message.author.mention + ", you are no longer a Kurzick.")
        else:
            await user.add_roles(role)
            await ctx.send(ctx.message.author.mention + ", welcome to the Kurzicks!")

    async def both_role(self, ctx):
        server = ctx.message.server
        channel = ctx.message.channel
        user = ctx.message.author
        role = discord.utils.get(server.roles, name="Kurz and Lux Alliances")

        if "Luxon" in user.roles:
            await user.remove_roles(role)
            await ctx.send(ctx.message.author.mention + ", you are no longer both a Kurzick and a Luxon.")
        else:
            await user.add_roles(role)
            await ctx.send(channel, ctx.message.author.mention + ", you sneaky devil, welcome to both sides of Cantha!")


    async def assign_luxon(self, ctx):
        message = ctx.message
        author = ctx.message.author
        channel = ctx.message.channel
        role_lgit_member = await self.role_add(ctx, "Discord Member")
        already_roled = await self.role_main(ctx, "Luxon")
        if already_roled is True:
            await ctx.send(author.mention + ", you are no longer a Luxon.")
        elif already_roled is False:
            await ctx.send(author.mention + ", welcome to LGiT and the Luxons!")

    @commands.command()
    async def luxon(self, ctx):
        """Assign/unassign Luxon role."""
        await self.assign_luxon(ctx)

    @commands.command()
    async def lux(self, ctx):
        """Assign/unassign Luxon role."""
        try:
            await self.assign_luxon(ctx)
        except Exception as e:
            await ctx.send(e)

    async def assign_kurzick(self, ctx):
        message = ctx.message
        author = ctx.message.author
        channel = ctx.message.channel
        role_lgit_member = await self.role_add(ctx, "Discord Member")
        already_roled = await self.role_main(ctx, "Kurzick")
        if already_roled is True:
            await ctx.send(author.mention + ", you are no longer a Kurzick.")
        elif already_roled is False:
            await ctx.send(author.mention + ", welcome to LGiT and the Kurzicks!")

    @commands.command()
    async def kurz(self, ctx):
        """Assign/unassign Kurzick role."""
        await self.assign_kurzick(ctx)

    @commands.command()
    async def kurzick(self, ctx):
        """Assign/unassign Kurzick role."""
        await self.assign_kurzick(ctx)

    @commands.command()
    async def both(self, ctx):
        """Assign/unassign the Kurz and Lux Alliance role."""
        role_lgit_member = await self.role_add(ctx, "Discord Member")
        already_roled_lux = await self.role_main(ctx, "Kurzick")
        already_roled_kurz = await self.role_main(ctx, "Luxon")
        if already_roled_lux is True and already_roled_kurz is True:
            await ctx.send(ctx.message.author.mention + ", you are no longer either Kurzick or Luxon.")
        elif already_roled_lux is False and already_roled_kurz is False:
            await ctx.send(ctx.message.author.mention + ", you sneaky devil, welcome to LGiT and both sides of Cantha!")
        elif already_roled_lux is True:
            await self.role_add(ctx, "Kurzick")
            await self.role_add(ctx, "Luxon")
            await ctx.send(ctx.message.author.mention + ", you were a Luxon and now you are a Kurzick too!.")
        elif already_roled_kurz is True:
            await self.role_add(ctx, "Kurzick")
            await self.role_add(ctx, "Luxon")
            await ctx.send(ctx.message.author.mention + ", you were a Kurzick and now you are Luxon too!")

    async def __local_check(self, ctx):
        if ctx.guild.id == 343067824979443722:
            return True
        else:
            return False