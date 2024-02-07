from discord import Interaction, app_commands
from discord.ext.commands import Bot, Cog


class Leave(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command(name="leave", description="Botをサーバーから退出させます")
    async def verify(self, ctx: Interaction):
        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message("このコマンドを実行する権限がありません",
                                            ephemeral=True)
            return

        await ctx.guild.leave()


def setup(bot: Bot):
    return bot.add_cog(Leave(bot))
