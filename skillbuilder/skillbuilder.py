from redbot.core.bot import Red
from redbot.core import checks
from discord.ext import commands
import discord

import os, sys
import base64
import time
import asyncio
from io import BytesIO
import datetime
from PIL import Image
import json
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import math

import pprint
import re
import random
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor

import sqlite3

def text_to_code(user_input):
    code = user_input
    if user_input.find(";") != -1:
        pos_start = user_input.find(";") + 1
        end_bracket_pos = user_input.find("]")
        if end_bracket_pos != -1:
            code = user_input[pos_start:end_bracket_pos]
        else:
            code = user_input[pos_start:]
        template_name = user_input[1:pos_start-1]
    else:
        template_name = None
    return code, template_name

def decode_base64(code):
    missing_padding = (4 - (len(code) % 4)) % 4
    code += 'A'* (missing_padding)
    return base64.b64decode(code)

def code_to_strflipped(code):
    bytes_obj = decode_base64(code)
    int_large = int.from_bytes(bytes_obj, byteorder='big')
    binary_str = "00" + bin(int_large)[2:]
    array = re.findall("......",binary_str)
    i = 0
    for group in array:
        group = group[::-1]
        array[i] = group
        i += 1
    strflipped = ''.join(array)
    return strflipped

def strflipped_to_code(strflipped):
    strflipped = strflipped + "0"*(168 - len(strflipped))
    array = re.findall("......",strflipped)
    i = 0
    for group in array:
        group = group[::-1]
        array[i] = group
        i += 1
    binary_str = "".join(array)
    binary_str = binary_str[2:]
    int_large = int(binary_str, 2)
    bytes_obj = int_large.to_bytes((int_large.bit_length() // 8) + 1, byteorder='big')
    base64_code = base64.b64encode(bytes_obj)
    code = str(base64_code)[2:-1]
    if code.endswith("AAAA"):
        code = code[:-4]
    return code

def code_to_build(code, original_code=None):
    build = {}
    if original_code is None:
        original_code = code
    build["original_code"] = original_code
    strflipped = code_to_strflipped(code)

    build["code"] = code
    build["template type"] = int(strflipped[0:4][::-1],2)
    build["version number"] = int(strflipped[4:8][::-1],2)

    build["professions"] = {}
    build["professions"]["control"] = int(strflipped[8:10][::-1],2) # Number of encoded bits per profession code
    professions_code_size = build["professions"]["control"] * 2 + 4
    xpos = 10
    ypos = xpos + professions_code_size
    build["professions"]["primary"] = {}
    build["professions"]["primary"]["id"] = int(strflipped[xpos:ypos][::-1],2)
    build["professions"]["primary"]["name"] = prof_reference[str(build["professions"]["primary"]["id"])]
    xpos = ypos
    ypos = xpos + professions_code_size
    build["professions"]["secondary"] = {}
    build["professions"]["secondary"]["id"] = int(strflipped[xpos:ypos][::-1],2)
    build["professions"]["secondary"]["name"] = prof_reference[str(build["professions"]["secondary"]["id"])]

    build["attrbs"] = {}
    xpos = ypos
    ypos = xpos + 4
    build["attrbs"]["count"] = int(strflipped[xpos:ypos][::-1],2)
    xpos = ypos
    ypos = xpos + 4
    build["attrbs"]["control"] = int(strflipped[xpos:ypos][::-1],2) # Number of encoded bits per attribute id
    attributes_code_size = build["attrbs"]["control"] + 4

    for i in range(1, build["attrbs"]["count"]+1):
        xpos = ypos
        ypos = xpos + attributes_code_size
        build["attrbs"][i] = {}
        build["attrbs"][i]["id"] = int(strflipped[xpos:ypos][::-1],2)
        build["attrbs"][i]["name"] = attrb_reference[str(build["attrbs"][i]["id"])]
        xpos = ypos
        ypos = xpos + 4
        build["attrbs"][i]["points"] = int(strflipped[xpos:ypos][::-1],2)

    xpos = ypos
    ypos = xpos + 4
    build["skills"] = {}
    build["skills"]["control"] = int(strflipped[xpos:ypos][::-1],2) # Number of encoded bits per skill id
    skills_code_size = build["skills"]["control"] + 8

    for i in range(1, 8+1):
        xpos = ypos
        ypos = xpos + skills_code_size
        build["skills"][i] = {}
        build["skills"][i]["id"] = int(strflipped[xpos:ypos][::-1],2)
        build["skills"][i]["name"] = skill_reference[str(build["skills"][i]["id"])]["Name"]

    return build

def pad_binary(input, req_length):
    length = len(input)
    output = "0" * (req_length - length) + input
    return output

def int_to_binary_str(int_value, req_length):
    str_int = "{0:b}".format(int_value)
    str_int = str_int.replace("0b","")
    output = pad_binary((str_int), req_length)
    output = output[::-1]
    return output

def build_to_code(build):
    # Update controls
    # Attributes count
    build["attrbs"]["count"] = len(build["attrbs"]) - 2

    # Attributes control
    attrb_ids = []
    for i in range(1, len(build["attrbs"]) - 1):
        attrb_ids.append(build["attrbs"][i]["id"])

    if len(attrb_ids) > 0:
        max_attrb_id = int(max(attrb_ids))
    else:
        max_attrb_id = 0
    if max_attrb_id > 31:
        build["attrbs"]["control"] = 2
    elif max_attrb_id > 15:
        build["attrbs"]["control"] = 1
    else:
        build["attrbs"]["control"] = 0

    # Skills control
    max_points = [255, 511, 1023, 2047]
    skill_ids = []
    for i in range(1, 8+1):
        skill_ids.append(build["skills"][i]["id"])
    i = 0
    build["skills"]["control"] = 0
    for max_point in max_points:
        if max(skill_ids) > max_point:
            build["skills"]["control"] = i + 1
        i += 1


    new_binary_str = ""

    # Template headers: type and version
    selection = build["template type"]
    new_binary_str = new_binary_str + int_to_binary_str(selection, 4)
    selection = build["version number"]
    new_binary_str = new_binary_str + int_to_binary_str(selection, 4)

    # Professions control
    selection = build["professions"]["control"]
    new_binary_str = new_binary_str + int_to_binary_str(selection, 2)

    # Professions
    professions_code_size = build["professions"]["control"] * 2 + 4

    selection = build["professions"]["primary"]["id"]
    new_binary_str = new_binary_str + int_to_binary_str(selection, professions_code_size)

    selection = build["professions"]["secondary"]["id"]
    new_binary_str = new_binary_str + int_to_binary_str(selection, professions_code_size)

    # Attributes count and control
    selection = build["attrbs"]["count"]
    new_binary_str = new_binary_str + int_to_binary_str(selection, 4)

    selection = build["attrbs"]["control"]
    new_binary_str = new_binary_str + int_to_binary_str(selection, 4)
    attributes_code_size = build["attrbs"]["control"] + 4

    # Attributes
    for i in range(1, build["attrbs"]["count"]+1):
        selection = build["attrbs"][i]["id"]
        new_binary_str = new_binary_str + int_to_binary_str(selection, attributes_code_size)
        selection = build["attrbs"][i]["points"]
        new_binary_str = new_binary_str + int_to_binary_str(selection, 4)

    # Skills control
    selection = build["skills"]["control"]
    new_binary_str = new_binary_str + int_to_binary_str(selection, 4)

    skills_code_size = build["skills"]["control"] + 8
    largest_skill_id = 0
    for i in range(1, 8+1):
        selection = build["skills"][i]["id"]
        new_binary_str = new_binary_str + int_to_binary_str(selection, skills_code_size)
    code = strflipped_to_code(new_binary_str)

    return code

def flip_dict(original):
    flipped_dict = {}
    for key in original.keys():
        flipped_dict[original[key]] = int(key)
    return flipped_dict

start_phrase = " -- `"
end_of_code_identifier = "` -- <:Template:384823463644233731>"
end_of_attrb_identifier = "   "
skill_reactions_msg = "\nUse reactions for skill descriptions. :point_down:"
adrenaline_emoji = "<:Adrenaline:388335958002630658>"
energy_emoji = "<:Energy:384819524244865035>"
activation_emoji = "<:Activation:384819522596765697>"
recharge_emoji = "<:Recharge:384819522693103627>"
overcast_emoji = "<:Overcast:384828799424004127>"

path = os.path.dirname(os.path.abspath(__file__))
data_dir = path + "/data"
with open("{}/skill_reference.json".format(data_dir)) as f:
    skill_reference = json.loads(f.read())
with open("{}/emoji_reference.json".format(data_dir)) as f:
    emoji_reference = json.loads(f.read())
with open("{}/attrb_reference.json".format(data_dir)) as f:
    attrb_reference = json.loads(f.read())
with open("{}/prof_reference.json".format(data_dir)) as f:
    prof_reference = json.loads(f.read())
with open("{}/skillslist_lower.json".format(data_dir)) as f:
    skillslist_lower = json.loads(f.read())
with open("{}/skillslist.json".format(data_dir)) as f:
    skillslist = json.loads(f.read())
with open("{}/skillsnumber.json".format(data_dir)) as f:
    skillsnumber = json.loads(f.read())

attrb_name_list = list(attrb_reference.values())
attrb_reverse_reference = flip_dict(attrb_reference)
prof_name_list = list(prof_reference.values())
prof_reverse_reference = flip_dict(prof_reference)

skillslist = tuple(skillslist)
skillsnumber = tuple(skillsnumber)
attrb_name_list = tuple(attrb_name_list)
prof_name_list = tuple(prof_name_list)


def build_to_message(build, skill_number=None):
    code = build["code"]

    pri_prof = build["professions"]["primary"]["name"]
    sec_prof = build["professions"]["secondary"]["name"]

    pri_emoji = "{}".format(emoji_reference[pri_prof])
    sec_emoji = "{}".format(emoji_reference[sec_prof])
    prof_msg = "{}**{}**/**{}**{}".format(pri_emoji, pri_prof, sec_prof, sec_emoji)

    attrb_msg = ""
    number_of_attributes = len(build["attrbs"])- 2 # Ignore "count" and "control"
    for i in range(1, number_of_attributes+1):
        attrb_name = build["attrbs"][i]["name"]
        attrb_points = build["attrbs"][i]["points"]
        attrb_msg += "{}: **{}**, ".format(attrb_name, attrb_points)
    attrb_msg = attrb_msg[:len(attrb_msg)-2]

    if skill_number is not None:
        skill_id = build["skills"][skill_number]["id"]
        skill_name = skill_reference[str(skill_id)]["Name"]
        skill_url = "https://wiki.guildwars.com/wiki/" + skill_name.replace(" ", "_")

        summary = skill_reference[str(skill_id)].get("Summary")
        fullstop_pos = summary.find(".")
        skill_summary = "*" + summary[:fullstop_pos+1] + "*" + summary[fullstop_pos+1:]
        skill_reactions_msg = "Skill {}: **{}** -- <{}>\n{}\n".format(skill_number, skill_name, skill_url, skill_summary)
        
        summary, attribute, activation, recharge, energy, profession, skill_type, overcast = "", "", "", "", "", "", "", ""
        attribute = skill_reference[str(skill_id)].get("Attribute")
        activation = skill_reference[str(skill_id)].get("Activation")
        recharge = skill_reference[str(skill_id)].get("Recharge")
        energy = skill_reference[str(skill_id)].get("Energy")
        adrenaline = skill_reference[str(skill_id)].get("Adrenaline")
        profession = skill_reference[str(skill_id)].get("Profession")
        skill_type = skill_reference[str(skill_id)].get("Skill Type")
        overcast = skill_reference[str(skill_id)].get("Overcast")

        if adrenaline is not None:
            skill_reactions_msg = "{} {}{}".format(skill_reactions_msg, adrenaline, adrenaline_emoji)
        if energy is not None:
            skill_reactions_msg = "{} {}{}".format(skill_reactions_msg, energy, energy_emoji)
        if activation is not None:
            skill_reactions_msg = "{} {}{}".format(skill_reactions_msg, activation, activation_emoji)
        if recharge is not None:
            skill_reactions_msg = "{} {}{}".format(skill_reactions_msg, recharge, recharge_emoji)
        if overcast is not None:
            skill_reactions_msg = "{} {}{}".format(skill_reactions_msg, overcast, overcast_emoji)
        if profession is not None:
            skill_reactions_msg = "{} Prof: **{}**.".format(skill_reactions_msg, profession)
        if attribute is not None:
            skill_reactions_msg = "{} Attrb: **{}**.".format(skill_reactions_msg, attribute)
        if skill_type is not None:
            skill_reactions_msg = "{} Type: **{}**.".format(skill_reactions_msg, skill_type)

    else:
        skill_reactions_msg = "Use reactions for skill descriptions. :point_down:"

    build_msg = "{} -- `{}{}\n{}{}\n\n{}".format(prof_msg, code, end_of_code_identifier, attrb_msg, end_of_attrb_identifier, skill_reactions_msg)
    return build_msg

def build_to_img(build):
    result = Image.new("RGB", (512, 64))
    for i in range(1, 9):
        skill_id = build["skills"][i]["id"]
        file_name = skillsnumber.index(skill_id)
        path = "{}/template/skills/".format(data_dir) +  str(file_name) + ".jpg"
        img = Image.open(path)
        img.thumbnail((512, 64), Image.ANTIALIAS)
        x = (i-1) * 64
        y = 0
        w, h = img.size
        result.paste(img, (x, y, x + w, y + h))
    output = BytesIO()
    result.save(output, format="JPEG")
    output.seek(0)
    result = output.read()
    bytesimage = BytesIO(result)
    code = build["code"]
    image = discord.File(bytesimage, str(code) + ".jpg")
    return image

def prev_build_msg_to_code(original_content):
    end_phrase = end_of_code_identifier
    start_pos = original_content.find(start_phrase)
    end_pos = original_content.find(end_phrase)
    code = original_content[start_pos + len(start_phrase):end_pos]
    return code

def rebuild_build(original_content):
    code = prev_build_msg_to_code(original_content)
    build = code_to_build(code)
    return build

def convert_image_team(build, team_image, build_number):
    result = Image.new("RGB", (512, 64))
    for i in range(1, 9):
        skill_id = build["skills"][i]["id"]
        file_name = skillsnumber.index(skill_id)
        path = "{}/template/skills/".format(data_dir) +  str(file_name) + ".jpg"
        img = Image.open(path)
        img.thumbnail((512, 64), Image.ANTIALIAS)
        x = (i-1) * 64
        y = 0
        w, h = img.size
        result.paste(img, (x, y, x + w, y + h))
    x = 0
    y = build_number * 64
    w = 512
    h = 64
    team_image.paste(result, (x, y, x + w, y + h))
    return team_image

def convert_to_bytes(team_image):
    output = BytesIO()
    team_image.save(output, format="JPEG")
    output.seek(0)
    team_image = output.read()
    bytesimage = BytesIO(team_image)
    return bytesimage

def rebuild_build_attrbs(build, i):
    total_attrbs = len(build["attrbs"].keys()) - 2
    del build["attrbs"][i]
    for x in range(i, total_attrbs):
        build["attrbs"][x] = build["attrbs"][x+1].copy()
        del build["attrbs"][x+1]
    return build

async def submit_to_executor(executor, build):
    future_build_msg = executor.submit(build_to_message, build)
    future_image = executor.submit(build_to_img, build)
    await asyncio.sleep(0)
    return future_build_msg.result(), future_image.result()

columns = ("name", "pri_prof", "sec_prof", "timestamp")

def archive_read():
    conn = sqlite3.connect("{}/archive.db".format(data_dir))
    c = conn.cursor()

    try:
        c.execute("CREATE TABLE archive (author_id, code, name, pri_prof, sec_prof, timestamp, PRIMARY KEY (author_id, code))")
    except sqlite3.OperationalError as e:
        print(e)

    c.execute("SELECT * FROM archive")
    rows = c.fetchall()

    archive = {}
    for row in rows:
        author_id = row[0]
        archive[author_id] = {}

    for row in rows:
        code = row[1]
        i = 2
        info_dict = {}
        for column in columns:
            info_dict[column] = row[i]
            i += 1
        archive[author_id][code] = info_dict

    conn.commit()
    conn.close()
    return archive

def archive_dump(archive):
    conn = sqlite3.connect("{}/archive.db".format(data_dir))
    c = conn.cursor()

    try:
        c.execute("CREATE TABLE archive (author_id, code, name, pri_prof, sec_prof, timestamp, PRIMARY KEY (author_id, code))")
    except sqlite3.OperationalError as e:
        print(e)

    rows = []
    for author_id, author_dict in archive.items():
        for code, code_dict in author_dict.items():
            row = []
            row.append(author_id)
            row.append(code)
            for column in columns:
                row.append(code_dict[column])
            rows.append(row)

    for row in rows:
        c.execute("INSERT OR REPLACE INTO archive VALUES (?, ?, ?, ?, ?, ?)", row)

    conn.commit()
    conn.close()

def archive_update(author_id, code, code_dict=None, mode="add or replace"):
    conn = sqlite3.connect("{}/archive.db".format(data_dir))
    c = conn.cursor()

    try:
        c.execute("CREATE TABLE archive (author_id, code, name, pri_prof, sec_prof, timestamp, PRIMARY KEY (author_id, code))")
    except sqlite3.OperationalError as e:
        print(e)

    if mode == "delete":
        c.execute("DELETE FROM archive WHERE author_id = ? and code = ?", (author_id, code))
    else:
        row = []
        row.append(author_id)
        row.append(code)
        for column in columns:
            row.append(code_dict[column])
        c.execute("INSERT OR REPLACE INTO archive VALUES (?, ?, ?, ?, ?, ?)", row)

    conn.commit()
    conn.close()

digit = {1:"\N{DIGIT ONE}\N{COMBINING ENCLOSING KEYCAP}",
    2:"\N{DIGIT TWO}\N{COMBINING ENCLOSING KEYCAP}",
    3:"\N{DIGIT THREE}\N{COMBINING ENCLOSING KEYCAP}",
    4:"\N{DIGIT FOUR}\N{COMBINING ENCLOSING KEYCAP}",
    5:"\N{DIGIT FIVE}\N{COMBINING ENCLOSING KEYCAP}",
    6:"\N{DIGIT SIX}\N{COMBINING ENCLOSING KEYCAP}",
    7:"\N{DIGIT SEVEN}\N{COMBINING ENCLOSING KEYCAP}",
    8:"\N{DIGIT EIGHT}\N{COMBINING ENCLOSING KEYCAP}"
    }

arrows = ["\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}", "\N{BLACK LEFT-POINTING TRIANGLE}", "\N{BLACK RIGHT-POINTING TRIANGLE}", "\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}"]

class InvalidResponse(Exception):
    pass

class SkillBuilder:
    """SkillBuilder!"""

    def __init__(self, bot):
        self.bot = bot
        self.cache = {}
        self.cache_message_objs = {}
        if sys.platform == "win32":
            print("I'm on windows")
            self.executor = ThreadPoolExecutor(max_workers=1)
        else:
            self.executor = ProcessPoolExecutor(max_workers=3)
        self._cd = commands.CooldownMapping.from_cooldown(10, 5, commands.BucketType.user)
        self.archive = archive_read()
        # try:
        #     with open("{}/archive.json".format(data_dir)) as f:
        #         self.archive = json.loads(f.read())
        # except Exception as e:
        #     print(e)
        #     self.archive = {}

    async def add_reactions(self, message):
        for skill_number in digit.keys():
            try:
                await message.add_reaction(digit[skill_number])
            except:
                pass

    async def add_arrows(self, message):
        for arrow in arrows:
            try:
                await message.add_reaction(arrow)
            except:
                pass

    def update_cache(self, build, build_msg, author_id, message_id, message_obj):
        build["author_id"] = author_id
        build["build_msg"] = build_msg
        self.cache[message_id] = build
        self.cache_message_objs[message_id] = message_obj

    async def skillbuilder_reaction_monitor(self, emoji, message_id, channel_id, user_id):
        # Check if reactions are being sent by the bot.
        if user_id == self.bot.user.id:
            return

        # Check if message is too old.
        time_of_message = discord.utils.snowflake_time(message_id)
        time_now = datetime.datetime.utcnow()
        time_limit = time_now - datetime.timedelta(days=30)
        if time_of_message < time_limit:
            return

        # Get message information.
        if message_id in self.cache:
            message_to_edit = self.cache_message_objs[message_id]
            channel = message_to_edit.channel
            guild = message_to_edit.guild
            original_content = message_to_edit.content
        else:
            channel = self.bot.get_channel(channel_id)
            guild = channel.guild
            message_to_edit = await channel.get_message(message_id)
            original_content = message_to_edit.content

        # Check if message to edit is a build message.
        if message_to_edit.author.id == self.bot.user.id and original_content.find("` -- ") != -1:
            reaction_emoji = emoji.name
        
            # Rebuild entry in cache if matching message id not found, otherwise, pull from cache.
            if message_id not in self.cache:
                build = rebuild_build(original_content)
            else:
                build = self.cache[message_id]

            # Get skill_number based on emoji chosen.
            for skill_number, emoji in digit.items():
                if reaction_emoji == emoji:
                    break

            # Construct build message
            build_msg = build_to_message(build, skill_number)
            
            # Edit message
            await message_to_edit.edit(content=build_msg)

            # Update cache
            self.update_cache(build, build_msg, user_id, message_id, message_to_edit)

    async def send_skill_build(self, ctx, user_input):
        code, template_name = text_to_code(user_input)
        try:
            build = code_to_build(code)
        except:
            await ctx.send("Oops! Looks like you did not send me a valid skill code.")
            return
        build_msg, image = await submit_to_executor(self.executor, build)
        message = await ctx.send(file=image)
        await message.edit(content=build_msg)
        self.update_cache(build, build_msg, ctx.author.id, message.id, message)
        await self.add_reactions(message)

    @commands.command()
    async def s(self, ctx, *, template_code: str):
        """Pings the build you entered. Accepts [xx;xyzcode123].

        -skill <template_code> OR -s <template_code>
        Example: -skill [Contagion_Necro;OAdDQTxGTbh0BMVrgINRCfBkiA]
        """
        await self.send_skill_build(ctx, template_code)

    @commands.command()
    async def skill(self, ctx, *, template_code: str):
        """Pings the build you entered. Accepts [xx;xyzcode123].

        -skill <template_code> OR -s <template_code>
        Example: -skill OAdDQTxGTbh0BMVrgINRCfBkiA
        Example: -skill [Contagion_Necro;OAdDQTxGTbh0BMVrgINRCfBkiA]
        """
        await self.send_skill_build(ctx, template_code)

    async def prev_msg_to_build(self, ctx):
        # Check for recent build.
        prev_command_msgs = []
        prev_build_msgs = []
        build_found = False
        async for prev_msg in ctx.channel.history(limit=200):
            if prev_msg.id in self.cache:
                if ctx.author.id == self.cache[prev_msg.id]["author_id"]:
                    build_found = True
                    build = self.cache[prev_msg.id]
                    return build, prev_msg

            # Build lists for comparison
            try:
                if prev_msg.author.id == self.bot.user.id and prev_msg.content.find("` -- ")!= -1 and len(prev_msg.attachments) == 1:
                    prev_build_msgs.append(prev_msg)
            except IndexError: # This means that there is no attachment. Still check for prev_command_msgs though.
                pass
            
            if ctx.author.id == prev_msg.author.id and (prev_msg.content.startswith(".s ") or prev_msg.content.startswith("-s ")):
                prev_command_msgs.append(prev_msg.content)

            # Check a maximum of 200 command messages
            if len(prev_command_msgs) > 200:
                break

        # Check recent history for corresponding commands.
        for prev_build_msg in prev_build_msgs:
            original_code = prev_build_msg.attachments[0].filename[:-4]
            for prev_command_msg in prev_command_msgs:
                if original_code in prev_command_msg:
                    try:
                        updated_code = prev_build_msg_to_code(prev_build_msg.content)
                        build = code_to_build(updated_code, original_code)
                        build_found = True
                        return build, prev_build_msg
                    except:
                        pass

        if build_found is False:
            raise InvalidResponse("No recent build found. Try pinging a new one.")

    async def fuzz_options(self, ctx, given_option, possible_options, to_delete):
            # Provide options using fuzzy wuzzy.
            options = process.extract(given_option, possible_options, limit=8)
            options_msg = "**Did you mean: **\n"
            i = 0
            for option in options:
                i += 1
                options_msg += "{}. {}\n".format(i, option[0])
            options_msg += "**Enter your new choice (1-8).**"
            fuzz_prompt = await ctx.send(options_msg)
            to_delete.append(fuzz_prompt)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                user_response = await self.bot.wait_for("message", check=check, timeout=60)
                to_delete.append(user_response)
            except asyncio.TimeoutError:
                raise InvalidResponse("Time's up.")
            
            try:
                new_choice = int(user_response.content.replace(".", "").replace(" ",""))
            except:
                raise InvalidResponse("You must provide a number between 1 and 8.")

            if new_choice > 0 and new_choice < 9:
                new_choice_name = options[new_choice-1][0]
                await fuzz_prompt.edit(content="\N{OK HAND SIGN} You chose: {}".format(new_choice_name))
                return new_choice_name, to_delete
            else:
                raise InvalidResponse("You must provide a number between 1 and 8.")

    async def edit_skill_build(self, ctx, skill_number, skill_name):
        to_delete = []
        to_delete.append(ctx.message)
        try:
            build, prev_msg = await self.prev_msg_to_build(ctx)

            # Check for valid skill number.
            if skill_number > 8 or skill_number < 1:
                raise InvalidResponse("Invalid skill number.")

            # Check if skill_name matches when lower-case. If so, convert to upper-case.
            if skill_name.lower() in skillslist_lower:
                skill_name = skillslist[skillslist_lower.index(skill_name.lower())]
            
            # If no match is found, send fuzz options.
            else:
                skill_name, to_delete = await self.fuzz_options(ctx, skill_name, skillslist, to_delete)

            # Modify build with chosen option.
            build["skills"][skill_number]["name"] = skill_name
            build["skills"][skill_number]["id"] = skillsnumber[skillslist.index(skill_name)]

            build["code"] = build_to_code(build)
            build_msg, image = await submit_to_executor(self.executor, build)
            await prev_msg.delete()
            new_message = await ctx.send(file=image)
            await new_message.edit(content=build_msg)
            try:
                del self.cache[prev_msg.id]
            except KeyError: # This is for situations where prev_msg was never cached
                pass
            self.update_cache(build, build_msg, ctx.author.id, new_message.id, new_message)
            await self.add_reactions(new_message)

        except InvalidResponse as e:
            error_msg = await ctx.send(e)
            to_delete.append(error_msg)
        finally:
            await asyncio.sleep(8)
            await ctx.channel.delete_messages(to_delete)

    async def edit_attrb_build(self, ctx, attrb_name, attrb_points):
        to_delete = []
        to_delete.append(ctx.message)
        try:
            build, prev_msg = await self.prev_msg_to_build(ctx)

            if attrb_points is not None:
                if attrb_points.find(" ") != -1:
                    end_string = attrb_points.split(" ")
                    if len(end_string) > 3:
                        raise InvalidResponse("'Uh... What? How many attribute points again?")
                    attrb_name = "{} {}".format(attrb_name, end_string[0])
                    attrb_name = attrb_name.title()
                    attrb_points = end_string[1]

                # Check for valid number given for attribute points.
                try:
                    attrb_points = int(attrb_points)
                    if attrb_points > 12:
                        raise InvalidResponse("You can only have a maximum of 12 attribute points!")
                except:
                    raise InvalidResponse("Invalid number for attribute points.\nTry again with: **-edit attrb {} {} <1-12>**".format(edit_type, attrb_name))

            attrb_name = attrb_name.title()

            # Check if valid attrb_name given.
            attrb_id = attrb_reverse_reference.get(attrb_name.title())

            # If not, send fuzz options.
            if attrb_id is None :
                attrb_name, to_delete = await self.fuzz_options(ctx, attrb_name, attrb_name_list, to_delete)
                attrb_id = attrb_reverse_reference.get(attrb_name)

            # Determine whether to add, edit or delete

            # Check if attribute points is zero
            if attrb_points == 0:
                edit_type = "del"

            else:

                # Check if attribute already exists
                no_attrb_found = True
                for i in range(1, len(build["attrbs"].keys())-1):
                    if build["attrbs"][i]["name"] == attrb_name:
                        no_attrb_found = False
                        break

                # If no attribute found, add. Otherwise, edit.
                if no_attrb_found is True:
                    edit_type = "add"
                elif no_attrb_found is False:
                    edit_type = "edit"

            if edit_type == "add":
                # Modify build according to option chosen
                i = len(build["attrbs"]) - 1
                current_attrbs_names = []
                for x in range(1, len(build["attrbs"].keys())-1):
                    current_attrbs_names.append(build["attrbs"][x]["name"])
                # if attrb_name in current_attrbs_names:
                #     raise InvalidResponse("You already have that attribute. Try editing instead with -edit attrb edit {} {}.".format(attrb_name, attrb_id))
                build["attrbs"][i] = {}
                build["attrbs"][i]["name"] = attrb_name
                build["attrbs"][i]["id"] = attrb_id
                build["attrbs"][i]["points"] = attrb_points

            elif edit_type == "edit":
                no_attrb_found = True
                for i in range(1, len(build["attrbs"].keys())-1):
                    if build["attrbs"][i]["name"] == attrb_name:
                        build["attrbs"][i]["name"] = attrb_name
                        build["attrbs"][i]["points"] = attrb_points
                        build["attrbs"][i]["id"] = attrb_id
                        no_attrb_found = False
                        break
                # if no_attrb_found is True:
                #     raise InvalidResponse("There is currently no such attribute in your build.")

            elif edit_type == "del":
                no_attrb_found = True
                for i in range(1, len(build["attrbs"].keys())-1):
                    if build["attrbs"][i]["name"] == attrb_name:
                        no_attrb_found = False
                        build = rebuild_build_attrbs(build, i)
                        break
                # if no_attrb_found is True:
                #     raise InvalidResponse("There is currently no such attribute in your build for you to delete.")

            build["code"] = build_to_code(build)

            # Since there is no need to send a new image when attributes are edited, this portion is actually unnecessary.
            build_msg, image = await submit_to_executor(self.executor, build)
            await prev_msg.delete()
            new_message = await ctx.send(file=image)
            await new_message.edit(content=build_msg)
            try:
                del self.cache[prev_msg.id] # This is for situations where prev_msg was never cached
            except KeyError:
                pass
            self.update_cache(build, build_msg, ctx.author.id, new_message.id, new_message)
            await self.add_reactions(new_message)

        except InvalidResponse as e:
            error_msg = await ctx.send(e)
            to_delete.append(error_msg)
        finally:
            await asyncio.sleep(8)
            await ctx.channel.delete_messages(to_delete)

    async def send_team_build(self, ctx, user_input):

        message_content = user_input
        open_bracket_count = user_input.count("[")

        if open_bracket_count > 0:
            print("more than 0")
            template_list = []
            templates_raw_list = message_content.split("]")
            i = 0
            for template in templates_raw_list:
                code = get_code(template)
                template_list.append(code)
                i += 1
                if i == open_bracket_count:
                    break
        else: 
            message_content = message_content.replace(",", " ")
            template_list = message_content.split()

        team_image = Image.new("RGB", (512, len(template_list)*64))

        if len(template_list) >= 1:

            # Send full team build
            build_number = 0
            while build_number < len(template_list):
                code = template_list[build_number]
                code, template_name = text_to_code(code)
                try:
                    build = code_to_build(code)
                except:
                    if (build_number + 1 == 1):
                        suffix = "st"
                    elif (build_number + 1 == 2):
                        suffix = "nd"
                    else:
                        suffix = "th"
                    await ctx.send("Oops! Looks like the **{}{}** code is not valid.".format(build_number + 1, suffix))
                    return

                # Compile image_team
                team_image = convert_image_team(build, team_image, build_number)
                build_number += 1

            bytesimage = convert_to_bytes(team_image)
            image = discord.File(bytesimage, "team_build_{}.jpg".format(datetime.datetime.utcnow()))
            await ctx.send(file=image)

    async def edit_prof_func(self, ctx, pri_or_sec, new_profession):
        to_delete = []
        to_delete.append(ctx.message)

        try:
            build, prev_msg = await self.prev_msg_to_build(ctx)

            pri_or_sec_options = ["pri", "primary", "sec", "secondary"]

            if pri_or_sec.lower() not in pri_or_sec_options:
                raise InvalidResponse("You must choose to edit either your primary or secondary profession.")

            index = pri_or_sec_options.index(pri_or_sec.lower())
            if index <= 1:
                pri_or_sec = "primary"
            elif index >= 2:
                pri_or_sec = "secondary"

            # Check if valid new_profession name given.
            new_profession = new_profession.title()
            prof_id = prof_reverse_reference.get(new_profession)
            if prof_id is None :
                new_choice_name, to_delete = await self.fuzz_options(ctx, new_profession, prof_name_list, to_delete)

            # Edit build
            prof_id = prof_reverse_reference.get(new_choice_name)
            build["professions"][pri_or_sec]["name"] = new_choice_name
            build["professions"][pri_or_sec]["id"] = prof_id
            build["code"] = build_to_code(build)
            build_msg, image = await submit_to_executor(self.executor, build)
            await prev_msg.delete()
            new_message = await ctx.send(file=image)
            await new_message.edit(content=build_msg)
            try:
                del self.cache[prev_msg.id] # This is for situations where prev_msg was never cached
            except KeyError:
                pass
            self.update_cache(build, build_msg, ctx.author.id, new_message.id, new_message)
            await ctx.message.delete()
            await self.add_reactions(new_message)

        except InvalidResponse as e:
            error_msg = await ctx.send(e)
            to_delete.append(error_msg)
        finally:
            await asyncio.sleep(8)
            await ctx.channel.delete_messages(to_delete)

    @commands.group()
    async def edit(self, ctx):
        """Edit the last build you pinged."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @edit.command(name="skill")
    async def edit_skill(self, ctx, skill_number: int, *, skill_name: str):
        """Edit skill. 

        -edit skill <skill_number> <skill_name>
        -es <skill_number> <skill_name>
        <skill number>: Choose which skill to modify (1 to 8).
        <skill name>: Select new skill.
        Example: -edit skill 7 Frenzy
        Example: -edit skill 8 Mending
        Quick command: -es"""
        await self.edit_skill_build(ctx, skill_number, skill_name)

    @edit.command(name="attrb")
    async def attrb(self, ctx, attrb_name, *, attrb_points):
        """Edit your attributes. 

        -edit attrb <attrb_name> <attrb_pts>
        -ea <attrb_name> <attrb_pts>
        Attribute will be deleted if attrb_pts = 0
        Example: -edit attrb Fast Casting 6 (add Fast Casting with 6 points if you don't already have it.)
        Example: -edit attrb Domination Magic 12 (change Domination Magic to 12 points if you already have it.)
        Example: -edit attrb Restoration Magic 0 (delete Restoration Magic entirely)
        Quick command: -ea"""
        await self.edit_attrb_build(ctx, attrb_name, attrb_points)
        # if ctx.invoked_subcommand is None or \
        #         isinstance(ctx.invoked_subcommand, commands.Group):
        #     await ctx.send_help()

        """
        <add/del/edit>: Choose to add, delete or edit your attributes.
        <attribute name>: Choose which attribute to add, delete or edit.
        <attribute points: Choose how many points to add or edit. Leave blank when deleting.
        """

    # @attrb.command(name="add")
    # async def _add_attrb(self, ctx, attrb_name, *, attrb_points):
    #     """Add attribute. Example: -edit attrb add Tactics 9"""
    #     await self.edit_attrb_build(ctx, attrb_name, attrb_points, "add")

    # @attrb.command(name="edit")
    # async def edit_attrb(self, ctx, attrb_name, *, attrb_points):
    #     """Edit attribute. Example: -edit attrb edit Domination Magic 10"""
    #     await self.edit_attrb_build(ctx, attrb_name, attrb_points, "edit")

    # @attrb.command(name="del")
    # async def del_attrb(self, ctx, *, attrb_name):
    #     """Delete attribute. Example: -edit attrb del Command 9"""
    #     attrb_points = None
    #     await self.edit_attrb_build(ctx, attrb_name, attrb_points, "del")

    @edit.command(name="prof")
    async def edit_prof(self, ctx, pri_or_sec: str, new_profession: str):
        """Edit profession. 

        -edit prof <pri_or_sec> <new_profession>
        <pri or sec>: Choose whether you want to modify your primary or secondary profession.
        <new profession>: Choose your new profession
        Example: -edit prof pri Warrior
        Example: -edit prof sec Monk"""
        await self.edit_prof_func(ctx, pri_or_sec, new_profession)

    @commands.command()
    async def t(self, ctx, *, user_input: str):
        """Ping team build. Skill codes should be separated by a comma.
        Accepts both xyzcode123 and [template;xyzcode123].
        Example: -t OAdDQTxGTbh0BMVrgINRCfBkiA, OAKjQugr1NYTr3jLcCNRuOzLG
        Example: -t [necro;OAdDQTxGTbh0BMVrgINRCfBkiA][rit;OAKjQugr1NYTr3jLcCNRuOzLG]
        Quick command: -t
        """
        await self.send_team_build(ctx, user_input)

    @commands.command()
    async def team(self, ctx, *, user_input: str):
        """Ping team build. Skill codes should be separated by a comma.
        Accepts both xyzcode123 and [template;xyzcode123].
        Example: -team OAdDQTxGTbh0BMVrgINRCfBkiA, OAKjQugr1NYTr3jLcCNRuOzLG
        Example: -team [necro;OAdDQTxGTbh0BMVrgINRCfBkiA][rit;OAKjQugr1NYTr3jLcCNRuOzLG]
        Quick command: -t
        """        
        await self.send_team_build(ctx, user_input)

    async def save_code(self, ctx, template_code):
        to_delete = []
        to_delete.append(ctx.message)

        try:
            author_id = str(ctx.author.id)

            try:
                total_builds_in_archive = len(self.archive[author_id].keys())
                if total_builds_in_archive >= 999:
                    raise InvalidResponse("Sorry, with {} builds saved, I believe you have set a record. This arbitrary limit was set by my creator a long time ago to prevent abuse. Now that you have succeeded in reaching this number, I applaud you. However, you cannot save any more. Delete one and try again.")
            except KeyError as e: # If author_id cannot be found in self.archive, there is no need for this check
                print(e)

            if template_code == "last" or template_code == None:
                interactive_prompt = await ctx.send("Okay, saving your last build...")
                to_delete.append(interactive_prompt)
                build, prev_msg = await self.prev_msg_to_build(ctx)
                code = build["code"]
                template_name = None
            else:
                try:
                    code, template_name = text_to_code(template_code)
                    build = code_to_build(code)
                    interactive_prompt = await ctx.send("Okay, saving `{}`...".format(code))
                    to_delete.append(interactive_prompt)
                except:
                    raise InvalidResponse("Sorry, you can only save valid skill codes.")

            if template_name is None:
                await interactive_prompt.edit(content="Please enter a name for your build in your next message.")

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                try:
                    build_name_msg = await self.bot.wait_for("message", check=check, timeout=60)
                    to_delete.append(build_name_msg)
                except asyncio.TimeoutError:
                    raise InvalidResponse("Time's up. Try again with a new command.")

                if len(build_name_msg.content) > 200:
                    build_name = build_name_msg.content[:200]
                    truncated_msg = await ctx.send("Wow that's a really long build name. I have truncated it for you to 200 char. It looks like this now: {}".format(build_name[:200]))
                    to_delete.append(truncated_msg)
                else:
                    build_name = build_name_msg.content

            else:
                build_name = template_name

            if author_id not in self.archive:
                self.archive[author_id] = {}
            else:
                self.archive[author_id][code] = {}
                self.archive[author_id][code]["name"] = build_name
                self.archive[author_id][code]["pri_prof"] = build["professions"]["primary"]["name"]
                self.archive[author_id][code]["sec_prof"] = build["professions"]["secondary"]["name"]
                self.archive[author_id][code]["timestamp"] = datetime.datetime.utcnow().timestamp()
            
            await interactive_prompt.edit(content="Done! Saved your code `{}` with the name: **{}**".format(code, build_name))

            # with open("{}/archive.json".format(data_dir), "w") as f:
            #     json.dump(self.archive, f)
            code_dict = self.archive[author_id][code]
            archive_update(author_id, code, code_dict, mode="add or replace")

        except InvalidResponse as e:
            error_msg = await ctx.send(e)
            to_delete.append(error_msg)
        finally:
            await asyncio.sleep(8)
            await ctx.channel.delete_messages(to_delete)

    @commands.command()
    async def save(self, ctx, *, template_code: str = None):
        """Save your build. Accepts [xx;xyzcode123].
        You can save up to 99 builds.
        Example: -save OAdDQTxGTbh0BMVrgINRCfBkiA
        Example: -save [Contagion_Necro;OAdDQTxGTbh0BMVrgINRCfBkiA]
        Quick command: -sv
        """
        await self.save_code(ctx, template_code)


    async def interactive_prompt_reaction_monitor(self, ctx, interactive_prompt, pages, current_page):

        def react_check(reaction, user):
            if user is None or user.id != ctx.author.id:
                return False

            if reaction.message.id != interactive_prompt.id:
                return False

            for arrow in arrows:
                if reaction.emoji == arrow:
                    return True
            return False

        try:
            while True:
                reaction, user = await self.bot.wait_for('reaction_add', check=react_check, timeout=120)

                for arrow in arrows:
                    if reaction.emoji == arrow:
                        break
                index = arrows.index(arrow)
                if index == 0: # Back to first page
                    current_page = 1
                    await interactive_prompt.edit(embed=pages[current_page-1])
                elif index == 1: # Previous page
                    if current_page != 1: # Not already the first page
                        current_page -= 1
                    await interactive_prompt.edit(embed=pages[current_page-1])
                elif index == 2: # Next page
                    if current_page != len(pages): # Not already the last page
                        current_page += 1
                    await interactive_prompt.edit(embed=pages[current_page-1])
                elif index == 3: # Last page
                    current_page = len(pages)
                    await interactive_prompt.edit(embed=pages[current_page-1])
                await interactive_prompt.remove_reaction(reaction.emoji, user)

        except asyncio.TimeoutError:
            raise InvalidResponse("Time's up. Try again with a new command.")

    async def build_selector_prompt(self, ctx, load_or_delete, build_number_or_name):
        to_delete = []
        to_delete.append(ctx.message)
        try:
            # Check for saved builds
            author_id = str(ctx.author.id)
            if author_id not in self.archive:
                raise InvalidResponse("Sorry, you don't have any builds saved.")

            # Set up lists
            saved_names = []
            saved_codes = []
            saved_pri_profs = []
            saved_sec_profs = []
            saved_timestamps = []

            for code in self.archive[author_id].keys():
                saved_names.append(self.archive[author_id][code]["name"])
                saved_codes.append(code)
                saved_pri_profs.append(self.archive[author_id][code]["pri_prof"])
                saved_sec_profs.append(self.archive[author_id][code]["sec_prof"])
                saved_timestamps.append(self.archive[author_id][code]["timestamp"])

            total_builds = len(self.archive[author_id].keys())


            # First two checks
            try:

                # Sort by timestamps
                indices = []
                for timestamp in sorted(saved_timestamps):
                    index = saved_timestamps.index(timestamp)
                    indices.insert(0, index)

                # Check if integer
                if build_number_or_name is not None:
                    build_number_or_name = int(build_number_or_name)
                    upper_limit = total_builds

                # Check if None
                elif build_number_or_name is None:

                    builds_per_page = 8
                    upper_limit = builds_per_page

                    # Sort by timestamp
                    choices_headers = []
                    choices_descriptions = []

                    # Generate paginated embed
                    i = 1
                    for index in indices:
                        name = saved_names[index]
                        pri_prof = saved_pri_profs[index]
                        sec_prof = saved_sec_profs[index]
                        choice_header = "**{}**. **{}/{}**".format(i, pri_prof, sec_prof)
                        choice_description = name
                        choices_headers.append(choice_header)
                        choices_descriptions.append(choice_description)
                        i += 1

                    pages = []
                    total_pages = math.ceil(total_builds/builds_per_page)
                    colour_value = random.randint(0, 16777215)
                    colour = discord.Colour(colour_value)
                    title = "Skill Builder -- Choose which build to {}, {}.".format(load_or_delete, ctx.author.name)
                    footer = "Enter a number between {} and {}.".format(1, total_builds)
                    for page_number in range(1, total_pages+1):
                        start_choice = (page_number - 1) * builds_per_page
                        end_choice = (page_number * builds_per_page)
                        description = "You are currently on page **{}** of **{}**.".format(page_number, total_pages)
                        embed = discord.Embed(title=title, description=description, colour=colour)
                        embed = embed.set_footer(text=footer)
                        for choice_header, choice_description in zip(choices_headers[start_choice:end_choice], choices_descriptions[start_choice:end_choice]):
                            embed = embed.add_field(name=choice_header, value=choice_description, inline=False)
                        pages.append(embed)

                    current_page = 1
                    interactive_prompt = await ctx.send(embed=pages[current_page-1])
                    to_delete.append(interactive_prompt)
                    self.bot.loop.create_task(self.add_arrows(interactive_prompt))

                    self.bot.loop.create_task(self.interactive_prompt_reaction_monitor(ctx, interactive_prompt, pages, current_page))

                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.channel

                    try:
                        msg = await self.bot.wait_for("message", check=check, timeout=120)
                        to_delete.append(msg)
                    except asyncio.TimeoutError:
                        raise InvalidResponse("Time's up. Try again with a new command.")

                    try:
                        new_choice = msg.content.replace(".", "").replace(" ","")
                        build_number_or_name = int(new_choice)
                    except:
                        raise InvalidResponse("You must provide a number between **{}** and **{}**.".format(1, total_pages))

                # Whether none or integer, continue here
                if build_number_or_name >= 1 and build_number_or_name <= total_builds:
                    index = indices[build_number_or_name-1]
                    code = saved_codes[index]
                    name = saved_names[index]
                    await ctx.send("\N{OK HAND SIGN} You chose to {} {}".format(load_or_delete, name))
                    if load_or_delete is "load":
                        await self.send_skill_build(ctx, code)
                    elif load_or_delete is "delete":
                        if total_builds == 1:
                            del self.archive[author_id]
                        else:
                            del self.archive[author_id][code]
                        # with open("{}/archive.json".format(data_dir), "w") as f:
                        #     json.dump(self.archive, f)
                        archive_update(author_id, code, mode="delete")
                else:
                    raise InvalidResponse("You must provide a number between **{}** and **{}**.".format(1, total_builds))


            # This means that it is a string, so give fuzz options
            except ValueError:
                new_choice_name, to_delete = await self.fuzz_options(ctx, build_number_or_name, saved_names, to_delete)
                upper_limit = 8
                index = saved_names.index(new_choice_name)
                code = saved_codes[index]

                await ctx.send("\N{OK HAND SIGN} You chose to {} {}".format(load_or_delete, new_choice_name))
                if load_or_delete is "load":
                    await self.send_skill_build(ctx, code)
                elif load_or_delete is "delete":
                    if total_builds == 1:
                        del self.archive[author_id]
                    else:
                        del self.archive[author_id][code]
                    archive_update(author_id, code, mode="delete")

        except InvalidResponse as e:
            error_msg = await ctx.send(e)
            to_delete.append(error_msg)
        finally:
            await asyncio.sleep(8)
            await ctx.channel.delete_messages(to_delete)

    @commands.command()
    async def load(self, ctx, *, build_number_or_name: str = None):
        """Load your build. Provide your build number to load or get a list of your builds.
        -load <build_number> OR -ld <build_number>
        -load <build_name> OR -ld <build_name>
        Only works if you already have builds saved.
        Example: -load 5
        Example: -load (this will start the interactive prompt)
        Example: -load Peter Kadar VoS
        Quick command: -ld
        """
        load_or_delete = "load"
        await self.build_selector_prompt(ctx, load_or_delete, build_number_or_name)

    @commands.command()
    async def delete(self, ctx, build_number: int = None):
        """Delete your build. Provide your build number to delete or get a list of your builds.
        -delete <build_number> OR -del <build_number>
        Be careful! Deletes are irreversible.
        Example: -delete 5
        Example: -delete (this will start the interactive prompt)
        Quick command: -del
        """
        load_or_delete = "delete"
        await self.build_selector_prompt(ctx, load_or_delete, build_number)

    @checks.is_owner()
    @commands.command()
    async def db(self, ctx):
        pprint.pprint(self.cache)
        await ctx.send(len(self.archive[str(ctx.author.id)].keys()))

    @checks.is_owner()
    @commands.command()
    async def saread(self, ctx):
        pprint.pprint(self.archive)
        await ctx.send(len(self.archive[str(ctx.author.id)].keys()))

    @checks.is_owner()
    @commands.command()
    async def adump(self, ctx):
        archive_dump(self.archive)

    @checks.is_owner()
    @commands.command()
    async def aread(self, ctx):
        self.archive = archive_read()
        pprint.pprint(self.archive)

    # async def __local_check(self, ctx):
    #     if ctx.guild is None:
    #         return False
    #     else:
    #         return True

    async def __global_check_once(self, ctx):
        bucket = self._cd.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after is None:
            return True
        else:
            await ctx.send("Please don't spam the bot. Thank you.")
            return False
