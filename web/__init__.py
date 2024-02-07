from discord.ext.commands import Bot

from web.app import App


def setup(bot: Bot):
    return bot.add_cog(App(bot))
