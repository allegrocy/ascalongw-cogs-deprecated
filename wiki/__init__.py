from .wiki import Wiki

def setup(bot):
    n = Wiki(bot)
    bot.add_cog(n)
