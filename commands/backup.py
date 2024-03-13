import logging

import requests
from discord import Interaction, app_commands
from discord.ext.commands import Bot, Cog

import config
from utils import VerifiedMember


class Backup(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command(name="backup", description="メンバーの復元を行います")
    async def verify(self, ctx: Interaction):
        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message("このコマンドを実行する権限がありません",
                                            ephemeral=True)
            return

        members = VerifiedMember.get()

        count = 0
        for i in members:
            member = ctx.guild.get_member(i.user_id)
            if member is None:
                # POST内容を指定
                request_post = {
                    "access_token": i.access_token
                }
                token_header = {
                    "Authorization": f"Bot {config.TOKEN}",
                    "Content-Type": "application/json"
                }

                # access_tokenを取得
                request = requests.put(
                    f"https://discordapp.com/api/guilds/{ctx.guild.id}/members/{i.user_id}",
                    json=request_post, headers=token_header)

                if request.status_code != 201:
                    logging.error(f"メンバー復元に失敗しました: {request.json()}")
                else:
                    count += 1

        await ctx.response.send_message(f"{count}人のメンバーを復元しました", ephemeral=True)

    @app_commands.command(name="check", description="復元可能なメンバー数をカウントします")
    async def check(self, ctx: Interaction):
        members = VerifiedMember.get()

        count = 0
        for i in members:
            member = ctx.guild.get_member(i.user_id)
            if member is None:
                count += 1

        await ctx.response.send_message(f"{count}人のメンバーが復元可能です", ephemeral=True)


def setup(bot: Bot):
    return bot.add_cog(Backup(bot))
