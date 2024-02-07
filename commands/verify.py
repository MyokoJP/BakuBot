import discord
from discord import Embed, Interaction, app_commands
from discord.ext.commands import Cog, Bot
from discord.ui import Button

import config
from utils import GiveRole


class Verify(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command(name="verify", description="認証メッセージを送信します")
    async def verify(self, ctx: Interaction):
        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message("このコマンドを実行する権限がありません", ephemeral=True)
            return

        guild = GiveRole.get(ctx.guild_id)
        if not guild:
            await ctx.response.send_message("付与するロールが設定されていません\n/rolesetで付与するロールを指定してください", ephemeral=True)
            return

        embed = Embed(
            title="認証",
            description="下のボタンを押して認証してください",
            color=discord.Color.green(),
        )

        await ctx.channel.send(embed=embed, view=self.ButtonView(ctx.guild_id))
        await ctx.response.send_message("認証メッセージを送信しました", ephemeral=True)

    class ButtonView(discord.ui.View):
        def __init__(self, guild_id: int):
            super().__init__(timeout=None)
            self.guild_id = guild_id

            button = Button(label="認証", style=discord.ButtonStyle.success, url=f"{config.OAUTH2_URL}&state={guild_id}")
            self.add_item(button)


def setup(bot: Bot):
    return bot.add_cog(Verify(bot))
