from .pricecheckaiohttp import PriceCheckAiohttp

def setup(bot):
    n = PriceCheckAiohttp(bot)
    bot.add_cog(n)
    bot.add_listener(n.pc_reaction_monitor, "on_raw_reaction_add")
    bot.add_listener(n.pc_reaction_monitor, "on_raw_reaction_remove")