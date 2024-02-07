from discord import Interaction, Role, app_commands
from discord.ext.commands import Bot, Cog

from utils import GiveRole


class RoleSet(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command(name="roleset", description="認証で付与するロールを設定します")
    async def roleset(self, ctx: Interaction, role: Role):
        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message("このコマンドを実行する権限がありません", ephemeral=True)
            return

        GiveRole.set(ctx.guild_id, role.id)
        await ctx.response.send_message("ロールを設定しました", ephemeral=True)


def setup(bot: Bot):
    return bot.add_cog(RoleSet(bot))
