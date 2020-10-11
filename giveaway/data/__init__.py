from .giveaway import Giveaway

def setup(bot):
    n = Giveaway(bot)
    bot.add_cog(n)

