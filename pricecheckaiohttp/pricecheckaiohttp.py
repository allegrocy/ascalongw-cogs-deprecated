import discord
from discord.ext import commands
from redbot.core import checks
import urllib
import aiohttp
import async_timeout
from bs4 import BeautifulSoup, SoupStrainer
import time
import asyncio
import datetime
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import sys

def parse(search_terms):
    search_string = urllib.parse.quote(search_terms)
    url = "https://kamadan.decltype.org/search/" + search_string
    return url

async def get_response(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    try:
        async with aiohttp.ClientSession() as session:
            with async_timeout.timeout(10):
                async with session.get(url, headers=headers) as response:
                    return await response.text()
    except asyncio.TimeoutError:
        error_message = "Oops! Either https://kamadan.decltype.org is down or this bot has gone on strike.\nTry searching directly on the website or at <#258069080869699586> (#Kamadan on the main Guild Wars discord)."
        raise RuntimeError(error_message) 

def append_am(author, authors, message, messages):
    if author is not None:
        len(author)
        authors.append(author)
    if message is not None:
        message = message.replace("```","")
        messages.append(message)
    return authors, messages

def get_info(htmlSource, mobile):

    authors, messages = [], []
    authors_temp = []

    only_tr_tags = SoupStrainer("tr")
    soup = BeautifulSoup(htmlSource, "html.parser", parse_only=only_tr_tags)

    first_row = soup.find("tr", {"class":"row"})
    author = first_row.find("div", {"class":"name"}).get_text()
    message = first_row.find("td", {"class":"message"}).get_text()
    authors_temp, messages = append_am(author, authors_temp, message, messages)

    for row in soup.find("tr",  {"class":"row"}).next_siblings:
        author = row.find("div", {"class":"name"}).get_text()
        message = row.find("td", {"class":"message"}).get_text()
        authors_temp, messages = append_am(author, authors_temp, message, messages)

    longest_length = len(max(authors_temp, key=len))

    for author in authors_temp:
        if mobile is True:
            author = "**{}**".format(author)
        else:
            pad_length = longest_length - len(author)
            padding = " " * pad_length
            author = padding + author
        authors.append(author)

    am_list = [authors, messages]

    return am_list

async def submit_to_executor(executor, htmlSource, mobile):
    future = executor.submit(get_info, htmlSource, mobile)
    await asyncio.sleep(0)
    result = future.result()
    return result[0], result[1]

def format_results(authors, messages, search_terms, page_number, url, results_length, t0, mobile):

    am_list = []
    for i in range(len(authors)):
        am_list.append(authors[i] + ": " + messages[i])
    t1 = time.time() - t0
    formatted_results = "\n".join(am_list)
    # search_time = "\n```Search took %.5f" % t1 + "s. Click below for more results."
    search_time = "\n```"
    search_time_str_length = len(search_time)
    formatted_results = "Search results for: **{}** (page {}) >> {} results per page\n{}\n```http\n{}".format(search_terms, page_number, results_length, url, formatted_results)
    formatted_results = formatted_results[:2000-search_time_str_length] + search_time
    if mobile is True:
        formatted_results = formatted_results.replace("```http\n","")
        formatted_results = formatted_results.replace("```","")

    return formatted_results

def round_up(value, round_up_to):
    remainder = (value * 8) % round_up_to
    if remainder == 0:
        result = int((value * 8) / round_up_to)
    else:
        result = int(((value * 8) + (round_up_to - remainder)) / round_up_to)
    return result

digit = {1:"\N{DIGIT ONE}\N{COMBINING ENCLOSING KEYCAP}",
    2:"\N{DIGIT TWO}\N{COMBINING ENCLOSING KEYCAP}",
    3:"\N{DIGIT THREE}\N{COMBINING ENCLOSING KEYCAP}",
    4:"\N{DIGIT FOUR}\N{COMBINING ENCLOSING KEYCAP}",
    5:"\N{DIGIT FIVE}\N{COMBINING ENCLOSING KEYCAP}",
    6:"\N{DIGIT SIX}\N{COMBINING ENCLOSING KEYCAP}",
    7:"\N{DIGIT SEVEN}\N{COMBINING ENCLOSING KEYCAP}",
    8:"\N{DIGIT EIGHT}\N{COMBINING ENCLOSING KEYCAP}"
    }

def parse_kamadan_logs(message_content, search_terms):
    kama_content = message_content[8:len(message_content)-4]
    kama_content_lines = kama_content.split("\n")
    logs_authors, logs_messages = [], []
    for kama_content_line in kama_content_lines:
        kama_author_end_pos = kama_content_line.find(":")
        kama_author = kama_content_line[:kama_author_end_pos]
        kama_message = kama_content_line[kama_author_end_pos+2:]
        if search_terms in kama_message:
            logs_authors.append(kama_author)
            logs_messages.append(kama_message)
    return logs_authors, logs_messages

def format_results_kamadan_logs(authors, messages, search_terms):
    am_list = []
    for i in range(len(authors)):
        am_list.append("{}: {}".format(authors[i], messages[i]))
    formatted_results = "\n".join(am_list)
    formatted_results = "Search results for: **{}**\n```http\n{}```".format(search_terms, formatted_results)
    formatted_results = formatted_results[:2000]
    return formatted_results

class PriceCheckAiohttp():
    """Price check, powered by kamadan.deceltype.com."""

    def __init__(self, bot):
        self.bot = bot
        self.init_datetime = datetime.datetime.utcnow()
        self.use_count = 0
        self.cache = {}
        if sys.platform == "win32":
            print("I'm on windows")
            self.executor = ThreadPoolExecutor(max_workers=1)
        else:
            self.executor = ProcessPoolExecutor(max_workers=3)

    def update_results(self, message_id, message_to_edit, page_number, results_length, t0, mobile):
        authors = self.cache[message_id]["authors"]
        messages = self.cache[message_id]["messages"]
        range_upper_end = page_number * results_length
        range_lower_end = range_upper_end - results_length
        if len(authors) < range_upper_end:
            range_upper_end = len(authors)
        authors = authors[range_lower_end:range_upper_end]
        messages = messages[range_lower_end:range_upper_end]
        search_terms = self.cache[message_id]["search_terms"]
        url = parse(search_terms)
        formatted_results = format_results(authors, messages, search_terms, page_number, url, results_length, t0, mobile)
        if len(authors) == 0:
            formatted_results = "No search results."
            formatted_results = "Search results for: **{}** (page {}) >> {} results per page\n{}\n```http\n{}```".format(search_terms, page_number, results_length, url, formatted_results)
            if mobile is True:
                formatted_results = formatted_results.replace("```http\n","")
                formatted_results = formatted_results.replace("```","")
        return formatted_results

    async def price_check(self, ctx, search_terms, results_length, mobile):
        """Main price check function"""
        t0 = time.time()
        search_terms = search_terms.replace("```", "")
        search_terms = search_terms.replace(") >> ", "")
        search_terms = search_terms.replace(" results per page__", "")
        search_terms = search_terms.replace("** (page ", "")
        page_number = 1
        authors, messages = None, None
        url = parse(search_terms)
        self.use_count += 1

        try:
            htmlSource = await get_response(url)
            # authors, messages = get_info(htmlSource, mobile)
            authors, messages = await submit_to_executor(self.executor, htmlSource, mobile)
            formatted_results = format_results(authors[:results_length], messages[:results_length], search_terms, page_number, url, results_length, t0, mobile)
            return formatted_results, authors, messages, search_terms

        except AttributeError:
            error_message = "No search results. Stop feeding me rubbish!"
            raise RuntimeError(error_message)

        except Exception as e:
            e_name = e.__class__.__name__
            if e_name == "ClientConnectorError":
                error_message = "Page failed to load. Site may be down. Try: " + url
                raise RuntimeError(error_message)
            else:
                error_message = "`{}`".format(e)
                raise RuntimeError(error_message)

    async def cache_more_results(self, message_id, authors, messages, search_terms, results_length, mobile):
        if authors is None:
            return
        try:
            if len(authors) == 25:
                max_pages = round_up(results_length, 25)
                tasks = []
                # print("Max pages = {}".format(max_pages))
                for page in range(1,max_pages):
                    # print("Page = {}".format(page))
                    length = page * 25
                    url = parse(search_terms)
                    url = url + "/" + str(length)
                    task = asyncio.ensure_future(get_response(url))
                    tasks.append(task)
                    # print("-----------APPENDING ONE TASK!")
                htmlSources = await asyncio.gather(*tasks)
                # for htmlSource in htmlSources:
                #     authors_next_page, messages_next_page = get_info(htmlSource, mobile)
                #     test_authors.extend(authors_next_page)
                #     test_messages.extend(messages_next_page)
                futures = []
                for htmlSource in htmlSources:
                    future = self.executor.submit(get_info, htmlSource, mobile)
                    futures.append(future)
                for future in futures:
                    authors_next_page, messages_next_page = future.result()
                    authors.extend(authors_next_page)
                    messages.extend(messages_next_page)
        except AttributeError:
            pass

        self.cache[message_id] = {}
        self.cache[message_id]["authors"] = authors
        self.cache[message_id]["messages"] = messages
        self.cache[message_id]["search_terms"] = search_terms
        self.last_message_id = message_id

    async def add_reactions(self, message):
        if message.author.id == self.bot.user.id and message.content.startswith("Search results for:"):
            message_to_react_to = message
        for skill_number in digit.keys():
            await message_to_react_to.add_reaction(digit[skill_number])

    async def pc_reaction_monitor(self, emoji, message_id, channel_id, user_id):
        if user_id == self.bot.user.id:
            return
        time_of_message = discord.utils.snowflake_time(message_id)
        time_now = datetime.datetime.utcnow()
        time_limit = time_now - datetime.timedelta(days=30)
        if time_of_message < time_limit:
            return
        channel = discord.utils.get(self.bot.get_all_channels(), id=channel_id)
        message_to_edit = await channel.get_message(message_id)
        if message_to_edit.author.id == self.bot.user.id and message_to_edit.content.find("Search results") != -1:
            reaction_emoji = emoji.name
            for page_number, emoji in digit.items():
                if reaction_emoji == emoji:
                    break

            message_header = message_to_edit.content[:message_to_edit.content.find("\n```http\n")]
            start_phrase = ") >> "
            start_pos = message_header.find(start_phrase)
            end_pos = message_header.find(" results per page")
            results_length = int(message_header[start_pos + len(start_phrase):end_pos])
            if message_to_edit.content.find("```") != -1:
                mobile = False
            else:
                mobile = True

            t0 = time.time()

            if message_to_edit.id in self.cache.keys():
                formatted_results = self.update_results(message_id, message_to_edit, page_number, results_length, t0, mobile)
            else:
                start_phrase = "Search results for: **"
                start_pos = message_header.find(start_phrase)
                end_pos = message_header.find("** (page ")
                search_terms = message_header[start_pos + len(start_phrase):end_pos]

                url = parse(search_terms)
                htmlSource = await get_response(url)
                # authors, messages = get_info(htmlSource, mobile)
                authors, messages = await submit_to_executor(self.executor, htmlSource, mobile)
                await self.cache_more_results(message_id, authors, messages, search_terms, results_length, mobile)
                formatted_results = self.update_results(message_id, message_to_edit, page_number, results_length, t0, mobile)
            if mobile is True:
                await message_to_edit.edit(content="Clearing previous message... This is necessary due to a bug with Discord's client.") 
            await message_to_edit.edit(content=formatted_results)
            self.use_count += 1

    @commands.group(invoke_without_command=True)
    async def pc(self, ctx, *, search_terms: str):
        """Perform price checks using https://kamadan.decltype.org."""
        results_length = 6
        mobile = False
        try:
            formatted_results, authors, messages, search_terms = await self.price_check(ctx, search_terms, results_length, mobile)
        except Exception as e:
            e = str(e)
            await ctx.send(e[1:-1])
            return
        message = await ctx.send(formatted_results)
        await self.cache_more_results(message.id, authors, messages, search_terms, results_length, mobile)
        await self.add_reactions(message)

    @pc.command(name="author")
    async def pc_author(self, ctx, *, search_terms: str):
        """Price check for a specific author."""
        mobile = False
        results_length = 6
        search_terms = "author:\"{}\"".format(search_terms.title())
        try:
            formatted_results, authors, messages, search_terms = await self.price_check(ctx, search_terms, results_length, mobile)
        except Exception as e:
            e = str(e)
            await ctx.send(e[1:-1])
            return        
        message = await ctx.send(formatted_results)
        await self.cache_more_results(message.id, authors, messages, search_terms, results_length, mobile)
        await self.add_reactions(message)

    @pc.command(name="m")
    async def pc_mobile(self, ctx, *, search_terms: str):
        """Formatted for mobile devices."""
        mobile = True
        results_length = 6
        try:
            formatted_results, authors, messages, search_terms = await self.price_check(ctx, search_terms, results_length, mobile)
        except Exception as e:
            e = str(e)
            await ctx.send(e[1:-1])
            return
        message = await ctx.send(formatted_results)
        await self.cache_more_results(message.id, authors, messages, search_terms, results_length, mobile)
        await self.add_reactions(message)

    @pc.command(name="mauthor")
    async def pc_mobile_author(self, ctx, *, search_terms: str):
        """Price check for a specific author on mobile."""
        mobile = True
        results_length = 6
        search_terms = "author:\"{}\"".format(search_terms.title())
        try:
            formatted_results, authors, messages, search_terms = await self.price_check(ctx, search_terms, results_length, mobile)
        except Exception as e:
            e = str(e)
            await ctx.send(e[1:-1])
            return
        message = await ctx.send(formatted_results)
        await self.cache_more_results(message.id, authors, messages, search_terms, results_length, mobile)
        await self.add_reactions(message)

    async def pc_bot_spam_only(self, ctx, search_terms, results_length, mobile):
        if ctx.channel.name == "bot-spam":
            try:
                formatted_results, authors, messages, search_terms = await self.price_check(ctx, search_terms, results_length, mobile)
            except Exception as e:
                e = str(e)
                await ctx.send(e[1:-1])
                return            
            message = await ctx.send(formatted_results)
            await self.cache_more_results(message.id, authors, messages, search_terms, results_length, mobile)
            await self.add_reactions(message)
        else:
            bot_spam = discord.utils.get(ctx.guild.channels, name="bot-spam")
            if bot_spam == None:
                await ctx.send("Sorry, you can only use this command in a channel with the name #bot-spam. Since you don't have one, you will need to ask your server administrators to set one up.")
            else:
                await ctx.send("Sorry, you can only use this command in <#{}>.".format(bot_spam.id))

    @pc.command(name="long")
    async def pc_long(self, ctx, *, search_terms: str):
        """More results! Can only be used in #bot-spam."""
        results_length = 25
        mobile = False
        await self.pc_bot_spam_only(ctx, search_terms, results_length, mobile)

    @pc.command(name="mlong")
    async def pc_mobile_long(self, ctx, *, search_terms: str):
        """Formatted for mobile devices. 25 search results."""
        results_length = 25
        mobile = True
        await self.pc_bot_spam_only(ctx, search_terms, results_length, mobile)

    @checks.is_owner()
    @commands.command()
    async def pcrep(self, ctx):
        """Report price check usage stats."""
        def strfdelta(tdelta, fmt):
            d = {"days": tdelta.days}
            d["hours"], rem = divmod(tdelta.seconds, 3600)
            d["minutes"], d["seconds"] = divmod(rem, 60)
            return fmt.format(**d)
        time_since_init = datetime.datetime.utcnow() - self.init_datetime
        time_since_init = strfdelta(time_since_init, "{days} days {hours}:{minutes}:{seconds}")
        await ctx.send("Price check commands. Used: **{}** times since **{}** ago.".format(self.use_count, time_since_init))

    @checks.is_owner()
    @commands.command()
    async def pcmlogs(self, ctx):
        self.history = []
        kamadan_channel = self.bot.get_channel(258069080869699586)
        async for message in kamadan_channel.history(limit=30000):
            self.history.append(message)
        await ctx.send("Logs retrieved.")

    @commands.command()
    async def pcm(self, ctx, *, search_terms: str):
        """Search using logs from #kamadan."""
        print("starting!")
        kamadan_channel = self.bot.get_channel(258069080869699586)
        search_results = []
        authors = []
        messages = []
        authors_temp = []
        try:
            for message in self.history:
                message_content = message.content
                if search_terms in message_content:
                    search_results.append(message_content)
                if len(search_results) > 10:
                    break
        except:
            async for message in kamadan_channel.history(limit=2000):
                message_content = message.content
                if search_terms in message_content:
                    search_results.append(message_content)
                if len(search_results) > 10:
                    break
        if len(search_results) == 0:
            await ctx.send("Sorry, no search results! Try something else.")
            return
        else:
            print("Number of search results = {}".format(len(search_results)))
            for search_result in search_results:
                logs_authors, logs_messages = parse_kamadan_logs(search_result, search_terms)
                for logs_author in logs_authors:
                    authors_temp.append(logs_author)
                for logs_message in logs_messages:
                    messages.append(logs_message)
            longest_length = len(max(authors_temp, key=len))
            for author in authors_temp:
                pad_length = longest_length - len(author)
                padding = " " * pad_length
                author = padding + author
                authors.append(author)
                print("Number of logs_authors = {}".format(len(logs_authors)))
        print("Number of authors = {}".format(len(authors)))
        formatted_results = format_results_kamadan_logs(authors, messages, search_terms)
        await ctx.send(formatted_results)
