from .skillbuilder import SkillBuilder

def setup(bot):
    n = SkillBuilder(bot)
    bot.remove_command("load")
    bot.add_cog(n)
    bot.add_listener(n.skillbuilder_reaction_monitor, "on_raw_reaction_add")
    bot.add_listener(n.skillbuilder_reaction_monitor, "on_raw_reaction_remove")