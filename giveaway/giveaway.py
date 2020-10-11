import discord
from discord.ext import commands
from redbot.core import checks
import asyncio
import json
import os
import datetime
import pprint
import random

# Standard strings
duration_instructions = (
    "Enter a duration in either hours or minutes. (Max: 3h)\n"
    "Example: `2h` for two hours OR `30m` for 30 minutes.\n")

integer_instructions = "Enter a number. Example: `5` not `five`"

role_instructions = (
    "Enter the name of the role that will be required to win.\n"
    "This is in addition to the default requirement of the @Giveaway role.\n"
    "Enter `none` for no additional role requirements.\n"
    "Example: `none` OR `pve` OR `pvp`")

error_warning = "What's wrong with you. Just follow the instructions I gave you. TRY AGAIN!"

def load_json(file_name):
    data_dir = os.path.dirname(os.path.abspath(__file__)) + "/data/"
    try:
        with open(data_dir + file_name, "r") as f:
            data = json.loads(f.read())
            print("Loaded {} successfully.".format(file_name))
    except Exception as e:
        print(e)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            print("Created directory: {}.".format(data_dir))
        data = {}
        with open(data_dir + file_name, "w") as f:
            json.dump(data, f)
            print("Created new file, {}, successfully.".format(file_name))
    return data

def dump_json(file_name, data):
    data_dir = os.path.dirname(os.path.abspath(__file__)) + "/data/"
    try:
        with open(data_dir + file_name, "w") as f:
            json.dump(data, f)
            print("Dumped to {} successfully.".format(file_name))
    except Exception as e:
        print(e)

def get_timedelta(ctx, giveaway_duration, error_message):
    msg_content = giveaway_duration.content.lower()
    end_pos = msg_content.find("h")
    if end_pos == -1:
        end_pos = msg_content.find("m")
        units = "minutes"
        if end_pos == -1:
            end_pos = len(msg_content)
    else:
        units = "hours"
    try:
        time_integer = int(msg_content[:end_pos])
        if units == "hours":
            if time_integer > 3:
                time_integer = 3
            timedelta = datetime.timedelta(hours=time_integer)
        elif units == "minutes":
            if time_integer > 180:
                time_integer = 180
            timedelta = datetime.timedelta(minutes=time_integer)
        return timedelta
    except ValueError:
        raise InvalidResponse(error_message)

def timedelta_to_str(timedelta):
    h, rem = divmod(timedelta.total_seconds(), 3600)
    m, s = divmod(rem, 60)
    h, m, s = int(h), int(m), int(s)
    if h == 0:
        confirmation_message = f"{m} minutes"
    elif m == 0:
        confirmation_message = f"{h} hours"
    else:
        confirmation_message = f"{h} hours and {m} minutes"
    return confirmation_message, h, m

def get_int(ctx, giveaway_limit, error_message):
    msg_content = giveaway_limit.content
    try:
        limit = int(msg_content)
        if limit < 1:
            raise InvalidResponse(error_message)
        return limit
    except ValueError:
        raise InvalidResponse(error_message)

class InvalidResponse(Exception):
    pass

class TimesUp(Exception):
    pass

class EnterError(Exception):
    pass

class EndError(Exception):
    pass

class Cancelled(Exception):
    pass

class Giveaway:
    """For hosting and organising giveaways."""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_json("data.json")
        self.lock = False
        for guild_id in self.data.keys():
            timeleft = self.data[guild_id]["end_timestamp"] - datetime.datetime.utcnow().timestamp()
            if timeleft > 0 and self.data[guild_id]["running"] is True:
                try:
                    self.bot.giveaway_tasks[guild_id].cancel()
                except:
                    pass
                task = asyncio.ensure_future(self.declare_winners(guild_id, timeleft))
                try:
                    self.bot.giveaway_tasks[guild_id] = task
                except:
                    self.bot.giveaway_tasks = {}
                    self.bot.giveaway_tasks[guild_id] = task

    def get_role(self, ctx, role_name, error_message):
        if role_name.content.lower() == "none":
            return "none"
        for role in ctx.guild.roles:
            if role.name.lower() == role_name.content.lower():
                return role
        raise InvalidResponse(error_message)

    async def get_response(self, ctx, timeout):
        try:
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            response = await self.bot.wait_for("message", check=check, timeout=timeout)
            return response

        except asyncio.TimeoutError:
            raise TimesUp(
                f"Time's up! You had **{timeout} seconds** but clearly that wasn't enough.\n"
                f"Don't give me that pathetic look, I'm not the one who types like a tortoise.")

    async def interactive_query(self, ctx, question, instructions, convert_func, max_attempts=5, timeout=60):
        question_message = f"{question}\n{instructions}"
        error_message = f"{error_warning}\n{instructions}"
        await ctx.send(question_message)
        for i in range(0, max_attempts):
            try:
                response = await self.get_response(ctx, timeout)
                if response.content.lower().find("cancel") != -1:
                    raise Cancelled("Your giveaway has been cancelled.")
                converted_response = convert_func(ctx, response, error_message)
                return converted_response
            except InvalidResponse as e:
                await ctx.send(e)
                if i == max_attempts - 1:
                    raise InvalidResponse(
                        f"This is attempt no. **{i+1}** and you're still giving me rubbish!\n"
                        f"Either learn to read instructions or find yourself another bot.\n"
                        f"I'm ending this session now so you will have to start over.")

    def running_check(self, guild_id=None):
        if guild_id not in self.data:
            self.data[guild_id] = {}
            self.data[guild_id]["running"] = False
        elif self.data[guild_id]["end_timestamp"] > datetime.datetime.utcnow().timestamp():
            self.data[guild_id]["running"] = True
        else:
            self.data[guild_id]["running"] = False

    async def declare_winners(self, guild_id, timeleft=None):

        if timeleft is not None:
            await asyncio.sleep(timeleft)

        guild = self.bot.get_guild(int(guild_id))
        channel = discord.utils.get(guild.channels, name="giveaways")
        # channel = discord.utils.get(guild.channels, name="test-channel")

        if len(self.data[guild_id]["entrants"]) == 0:
            await channel.send(
                "Since there are 0 entrants to this giveaway, no one won.\n"
                "Closing the giveaway now.")
        else:
            participants_list = []
            for entrant in self.data[guild_id]["entrants"]:
                member = guild.get_member(entrant)
                if member is not None:
                    for role in member.roles:
                        if role.name == "Giveaway":
                            participants_list.append(member)

            if len(participants_list) <= self.data[guild_id]["limit"]:
                winners_list = participants_list
            else:
                winners_list = random.sample(participants_list, k = self.data[guild_id]["limit"])

            mentions = ""
            for winner in winners_list:
                mentions += winner.mention + ", "
            mentions = mentions[:-2]

            creator = guild.get_member(self.data[guild_id]["creator_id"])
            prizes = self.data[guild_id]["prizes"]
            await channel.send(
                f"Congratulations, {mentions}.\n"
                f"You have won **{prizes}** in the giveaway by {creator.mention}!\n"
                f"Please provide your IGN and claim your prize in-game!")

    @commands.group(aliases=["g"])
    async def give(self, ctx):
        """Giveaway group command."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @give.command(aliases=["c"])
    async def create(self, ctx):
        """Create a giveaway."""
        guild_id = str(ctx.guild.id)
        self.running_check(guild_id)

        if self.data[guild_id]["running"] is True:
            await ctx.send("There can only be one giveaway at any time. Please wait until the current one has ended.")
            return
        try:
            start_timestamp = datetime.datetime.utcnow().timestamp()
            giveaway_role = discord.utils.get(ctx.guild.roles, name="Giveaway")
            giveaway_creator = ctx.author
            await ctx.send(
                f"ATTENTION EVERYONE, a new giveaway has been created by {giveaway_creator.mention}!\n"
                f"Such boundless generosity! So, {giveaway_creator.mention}, what are you giving away?\n"
                f"Please enter the giveaway items each individual winner will receive.\n")

            response = await self.get_response(ctx, 60)
            if response.content.lower().find("cancel") != -1:
                raise Cancelled("Your giveaway has been cancelled.")
            prizes = response.content
            await ctx.send(f"Awesome! Each winner will receive **{prizes}**.")

            question = "How long should the giveaway last?"
            duration = await self.interactive_query(ctx, question, duration_instructions, get_timedelta)
            duration_str, h, m = timedelta_to_str(duration)
            await ctx.send(f"Got it. The giveaway will last for **{duration_str}**")

            question = "How many people may win?"
            limit = await self.interactive_query(ctx, question, integer_instructions, get_int)
            await ctx.send(f"Noted. **{limit}** people stand a chance to win.")

            additional_role_str = ""
            # question = "Are there any role requirements?"
            # role_required = await self.interactive_query(ctx, question, role_instructions, self.get_role)
            # if role_required == "none":
            #     await ctx.send(f"Yes sir, there are no additional role requirements.")
            #     additional_role_str = ""
            # else:
            #     await ctx.send(f"Yes sir, only people with the **{role_required.name}** role can participate.")
            #     additional_role_str = f" and {role_required.name}"

            giveaway_announcement = (
                f"ATTENTION {giveaway_role.mention}, {giveaway_creator.mention} has started a giveaway!\n"
                f"Prizes: **{prizes}**\n"
                f"Duration: **{duration_str}**\n"
                f"Winners: **{limit}**\n"
                # f"Role required: {giveaway_role.mention}{additional_role_str}\n"
                f"`-enter` to register (you must have the @Giveaway role).\n"
                f"`-glist` for a list of all participants.\n"
                f"`-timeleft` for the remaining time.\n"
                f"`-ginfo` for information on the currently running giveaway.\n"
                f"Winners will be notified with a mention.")
            await ctx.send(giveaway_announcement)

            self.data[guild_id]["entrants"] = []
            self.data[guild_id]["giveaway_role_id"] = giveaway_role.id
            self.data[guild_id]["creator_id"] = giveaway_creator.id
            self.data[guild_id]["prizes"] = prizes
            self.data[guild_id]["duration"] = h, m
            self.data[guild_id]["limit"] = limit
            self.data[guild_id]["start_timestamp"] = start_timestamp
            self.data[guild_id]["end_timestamp"] = start_timestamp + (h * 3600) + (m * 60)

            dump_json("data.json", self.data)

            timeleft = self.data[guild_id]["end_timestamp"] - datetime.datetime.utcnow().timestamp()
            try:
                self.bot.giveaway_tasks[guild_id].cancel()
            except:
                pass
            task = asyncio.ensure_future(self.declare_winners(guild_id, timeleft))
            try:
                self.bot.giveaway_tasks[guild_id] = task
            except:
                self.bot.giveaway_tasks = {}
                self.bot.giveaway_tasks[guild_id] = task


        except InvalidResponse as e:
            await ctx.send(e)

        except TimesUp as e:
            await ctx.send(e)

        except Cancelled as e:
            await ctx.send(e)
        
    @commands.command()
    async def enter(self, ctx):
        """Enter the currently running giveaway."""
        guild_id = str(ctx.guild.id)
        self.running_check(guild_id)
        try:
            if self.data[guild_id]["running"] is False:
                raise EnterError("There is no giveaway running at the moment.")
            else:
                no_giveaway_role = True
                for role in ctx.author.roles:
                    if role.name == "Giveaway":
                        no_giveaway_role = False
                        break

                if no_giveaway_role is True:
                    raise EnterError(
                        "You need to have the @Giveaway role before you can enter.\n"
                        "Type `-giveaway` to give yourself the role.")

                if ctx.author.id in self.data[guild_id]["entrants"]:
                    raise EnterError(
                        "You have already been enrolled in the giveaway.\n"
                        "Type `-glist` for a list of all entrants.")

                else:
                    self.data[guild_id]["entrants"].append(ctx.author.id)
                    await ctx.send(f"Okay, {ctx.author.mention}, you have been enrolled in the giveaway.")

                    dump_json("data.json", self.data)

        except EnterError as e:
            await ctx.send(e)

    @commands.command()
    async def timeleft(self, ctx):
        """Check how much time is left on the current giveaway."""
        guild_id = str(ctx.guild.id)
        self.running_check(guild_id)
        try:
            if self.data[guild_id]["running"] is False:
                raise EndError("There is no giveaway running at the moment.")
            else:
                timeleft = self.data[guild_id]["end_timestamp"] - datetime.datetime.utcnow().timestamp()
                h, rem = divmod(timeleft, 3600)
                m, s = divmod(rem, 60)
                h, m, s = int(h), int(m), int(s)
                if h == 0:
                    timeleft_message = f"**{m}** minutes and **{s}** seconds till the giveaway ends!"
                else:
                    timeleft_message = f"**{h}** hours, **{m}** minutes and **{s}** seconds till the giveaway ends!"
                await ctx.send(timeleft_message)

        except EndError as e:
            await ctx.send(e)

    @commands.command()
    async def glist(self, ctx):
        """List all the entrants in the current giveaway."""
        guild_id = str(ctx.guild.id)
        self.running_check(guild_id)
        guild = self.bot.get_guild(int(guild_id))

        try:
            if self.data[guild_id]["running"] is False:
                raise EndError("There is no giveaway running at the moment.")
            else:
                participants_list = []
                for entrant in self.data[guild_id]["entrants"]:
                    member = guild.get_member(entrant)
                    if member is not None:
                        for role in member.roles:
                            if role.name == "Giveaway":
                                participants_list.append(member)

                participants_names = ""
                for participant in participants_list:
                    participants_names += participant.name + ", "

                participants_names = participants_names[:-2]
                length = len(participants_list)
                list_message = f"There are currently **{length}** participants. They are: {participants_names}."
                await ctx.send(list_message)

        except EndError as e:
            await ctx.send(e)

    @commands.command()
    async def ginfo(self, ctx):
        """Tells you what is being given out in the current giveaway."""
        guild_id = str(ctx.guild.id)
        self.running_check(guild_id)
        guild = self.bot.get_guild(int(guild_id))

        try:
            if self.data[guild_id]["running"] is False:
                raise EndError("There is no giveaway running at the moment.")
            else:
                number_of_entrants = len(self.data[guild_id]["entrants"])
                giveaway_creator_id = self.data[guild_id]["creator_id"]
                giveaway_creator = guild.get_member(giveaway_creator_id)
                prizes = self.data[guild_id]["prizes"]
                limit = self.data[guild_id]["limit"]

                timeleft = self.data[guild_id]["end_timestamp"] - datetime.datetime.utcnow().timestamp()
                h, rem = divmod(timeleft, 3600)
                m, s = divmod(rem, 60)
                h, m, s = int(h), int(m), int(s)
            if h == 0:
                timeleft = f"**{m}** minutes and **{s}** seconds!"
            else:
                timeleft = f"**{h}** hours, **{m}** minutes and **{s}** seconds!"

            ginfo_message = (
                f"Giveaway creator: {giveaway_creator.name}\n"
                f"Prizes: **{prizes}**\n"
                f"Time left: {timeleft}\n"
                f"Max winners: **{limit}**\n"
                f"Current entrants: **{number_of_entrants}**\n"
                f"`-enter` to register (you must have the @Giveaway role).\n"
                f"`-glist` for a list of all participants.\n"
                f"`-timeleft` for the remaining time.\n"
                f"`-ginfo` for information on the currently running giveaway.\n"
                f"Winners will be notified with a mention.")
            await ctx.send(ginfo_message)
        except EndError as e:
            await ctx.send(e)


    @checks.is_owner()
    @commands.command()
    async def endnow(self, ctx):
        """Ends the current giveaway now and declares the winners."""
        guild_id = str(ctx.guild.id)
        self.running_check(guild_id)
        try:
            if self.data[guild_id]["running"] is False:
                raise EndError("There is no giveaway running at the moment.")
            else:
                self.data[guild_id]["end_timestamp"] = 1
                await self.declare_winners(guild_id)
                await ctx.send("I have ended the current giveaway.")
                dump_json("data.json", self.data)
                self.bot.giveaway_tasks[guild_id].cancel()

        except EndError as e:
            await ctx.send(e)

    @checks.is_owner()
    @commands.command()
    async def force_cancel(self, ctx):
        """Cancels the current giveaway."""
        guild_id = str(ctx.guild.id)
        self.running_check(guild_id)
        try:
            if self.data[guild_id]["running"] is False:
                raise EndError("There is no giveaway running at the moment.")
            else:
                self.data[guild_id]["end_timestamp"] = 1
                await ctx.send("I have cancelled the current giveaway.")
                dump_json("data.json", self.data)
                self.bot.giveaway_tasks[guild_id].cancel()

        except EndError as e:
            await ctx.send(e)

    @checks.is_owner()
    @commands.command()
    async def pprint(self, ctx):
        """Display information on the giveaway data in console."""
        pprint.pprint(self.data)

