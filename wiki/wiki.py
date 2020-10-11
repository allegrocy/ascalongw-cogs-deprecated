import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import datetime
from googleapiclient.discovery import build
import aiohttp
import async_timeout
from urllib import parse

async def get_response(url):
    async with aiohttp.ClientSession() as session:
        with async_timeout.timeout(10):
            async with session.get(url) as response:
                return await response.text()

async def get_soup(url):
    htmlSource = await get_response(url)
    soup = BeautifulSoup(htmlSource, "html.parser")
    print ("You ran get_soup!")
    return soup

async def search_internal(searchstring, searchurl, siteprefix):
    searchstring = parse.quote_plus(searchstring)
    url = searchurl + searchstring
    soup = await get_soup(url)
    try:
        p = soup.find("p", "mw-search-exists")
        link = p.find("a")
        link = siteprefix + link["href"]
    except:
        try:
            div = soup.find("div", "mw-search-result-heading")
            link = div.find("a")
            link = siteprefix + link["href"]
        except:
            link = "No search result."
    return link

def google(searchstring, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=searchstring, cx=cse_id, **kwargs).execute()
    return res['items']

def search_google(searchstring, my_api_key, my_cse_id):
    results = google(searchstring, my_api_key, my_cse_id, num=1)
    result = results[0]
    print(result)
    link = result["link"]
    return link

def raise_exception(exception):
    if exception == True:
        raise ThrowException('Just testing...')

async def search(searchstring, searchurl, siteprefix, internal=False):
    try:
        raise_exception(internal)
        my_api_key = "AIzaSyB85PcU1K5IiQNkOFCUehu4iy_OwhmVt_0" #rampartrene
        my_cse_id = "008218372630222846078:mgjzssso8rs" # Wiki rampartrene
        link = search_google(searchstring, my_api_key, my_cse_id)
        print ("Google 1 returns: " + link)
    except:
        print ("fail 1")
        try:
            raise_exception(internal)
            my_api_key = "AIzaSyCsrv3a7jvmxrb63ETHZdkNtdoo5FO70Ec" #forald
            my_cse_id = "000324135811109807532:uuvhup1r9jo" # Wiki forald
            link = search_google(searchstring, my_api_key, my_cse_id)
            print ("Google 2 returns: " + link)
        except:
            print ("fail 2")
            link = await search_internal(searchstring, searchurl, siteprefix)
            print ("Internal search returns: " + link)
    return link

async def getinfo(url, characterlimit):

    soup = await get_soup(url)
    title = soup.title.get_text()
    pos = title.find(" - Guild Wars Wiki")
    title = title[:pos]
    try:
        summary = soup.p.get_text()
        rest = soup.find_all("p")
        detailed = ""
        i = 0
        while i < len(rest):
            detailed += rest[i].get_text()
            i = i + 1
        detailed_truncated = detailed[:characterlimit] + "..."
        detailed_truncated = detailed_truncated.replace("\n", " ")
    except:
        rest = soup.find_all("div", {"id":"mw-content-text"})
        if soup.get_text().find("This disambiguation page lists articles associated with the same title.") > -1:
            startpos = 185
        else:
            startpos = 0
        detailed = ""
        i = 0
        while i < len(rest):
            detailed += rest[i].get_text()
            i = i + 1
        detailed_truncated = detailed[startpos:characterlimit] + "..."
        detailed_truncated = detailed_truncated.replace("\n", " ")

    bot_message = "**__" + title + "__**\n" + "<" + url + ">\n```" + detailed_truncated+ "```"
    return bot_message

def setup(bot):
    bot.add_cog(Wiki(bot))

class Wiki():
    """Search Wiki"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def wiki(self, ctx, *args):
        """Gets info from wiki, uses Google search."""
        timestart = datetime.datetime.utcnow()
        i = 0
        searchstring = ""
        if len(args) > 1:
            while i < len(args):
                searchstring = searchstring + " " + args[i] + " "
                i = i + 1
        else:
            searchstring = args[i]
        searchstring = parse.quote_plus(searchstring)
        print(searchstring)
        searchurl = "https://wiki.guildwars.com/index.php?title=Special%3ASearch&profile=default&fulltext=Search&search="
        siteprefix = "https://wiki.guildwars.com"
        internal = False
        url = await search(searchstring, searchurl, siteprefix, internal)
        if url == "No search result.":
             await ctx.send(url)
        else:
            bot_message = await getinfo(url, 400)
            print (bot_message)
            await ctx.send(bot_message)

    @commands.command()
    async def wikim(self, ctx, *args):
        """Gets info from wiki, uses manual internal search."""
        timestart = datetime.datetime.utcnow()
        i = 0
        searchstring = ""
        if len(args) > 1:
            while i < len(args):
                searchstring = searchstring + " " + args[i] + " "
                i = i + 1
        else:
            searchstring = args[i]
        searchstring = parse.quote_plus(searchstring)
        print(searchstring)
        searchurl = "https://wiki.guildwars.com/index.php?title=Special%3ASearch&profile=default&fulltext=Search&search="
        siteprefix = "https://wiki.guildwars.com"
        internal = True
        url = await search(searchstring, searchurl, siteprefix, internal)
        if url == "No search result.":
             await ctx.send(url)
        else:
            bot_message = await getinfo(url, 400)
            print (bot_message)
            await ctx.send(bot_message)

    @commands.command()
    async def nickfarm2(self, ctx):
        """Gives you a link to the week's Nick farming guide"""
        url = "https://wiki.guildwars.com/wiki/Nicholas_the_Traveler"
        htmlSource = await get_soup(url)
        htmlSource = htmlSource.decode("utf8")
        pos1 = htmlSource.find("http://gwpvx.gamepedia.com/Guide:Nicholas_the_Traveler_Farming/")
        webpage_rest = htmlSource[pos1:]
        pos2 = webpage_rest.find("farming guide") - 2
        url = webpage_rest[:pos2]
        url = url[:url.find("\" rel=\"nofollow\">")]
        await ctx.send(url)
