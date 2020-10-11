from .selfrole import Selfrole

def setup(bot):
    n = Selfrole(bot)
    bot.add_cog(n)
    bot.add_listener(n.selfrole_monitor, "on_message")
    
