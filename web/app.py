import asyncio
import logging
import threading
import traceback

import discord
import requests
from discord.ext.commands import Bot, Cog
from flask import Flask, render_template, request
from waitress import serve

import config
from utils import GiveRole, VerifiedMember


class App(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

        self.app = Flask(__name__, root_path="./web")

        @self.app.route('/')
        def index():
            code = request.args.get("code", None)
            if not code:
                return render_template("index.html", title="エラーが発生しました",
                                       message="403 Forbidden")
            state = request.args.get("state", None)
            if not state:
                return render_template("index.html", title="エラーが発生しました",
                                       message="403 Forbidden")

            try:
                state = int(state)
            except ValueError:
                return render_template("index.html", title="エラーが発生しました",
                                       message="403 Forbidden")

            # POST内容を指定
            request_post = {
                "client_id": config.CLIENT_ID,
                "client_secret": config.CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": config.REDIRECT_URL,
            }

            # access_tokenを取得
            token_request = requests.post("https://discordapp.com/api/oauth2/token",
                                          data=request_post)

            # StatusCodeが200でなかったらエラーを表示
            if token_request.status_code != 200:
                logging.error(
                    f"access_tokenを取得できませんでした(Error: {token_request.json()}, Code: {code})"
                )

                return render_template("index.html", title="エラーが発生しました",
                                       message="もう一度お試しください")

            # access_tokenを指定
            access_token = token_request.json()["access_token"]
            refresh_token = token_request.json()["refresh_token"]
            expires_in = token_request.json()["expires_in"]

            # tokenからユーザーの情報を取得
            token_header = {"Authorization": f"Bearer {access_token}"}

            # tokenから参加サーバーを取得
            user = requests.get("https://discordapp.com/api/users/@me", headers=token_header)

            # Discordサーバーに参加しているかを確認
            user_id = int(user.json()["id"])

            # ロールを追加
            future = asyncio.run_coroutine_threadsafe(
                self.add_role(user_id, state),
                bot.loop
            )
            if not future.result():
                return render_template("index.html", title="エラーが発生しました",
                                       message="もう一度お試しください")

            # DBにユーザー情報を登録
            VerifiedMember.add(state, user_id, access_token, refresh_token, expires_in)

            return render_template("index.html", title="認証が完了しました！",
                                   message="このページは閉じても構いません")
        if config.WEB_DEBUG:
            t = threading.Thread(
                target=self.app.run,
                kwargs={"port": config.WEB_PORT, "debug": config.WEB_DEBUG, "use_reloader": False,
                        "threaded": False, "host": "0.0.0.0"},
                daemon=True
            )
        else:
            t = threading.Thread(
                target=serve,
                args=(self.app,),
                kwargs={"port": config.WEB_PORT, "host": "0.0.0.0"},
                daemon=True
            )

        t.start()

    async def add_role(self, user, guild_id):
        guild = self.bot.get_guild(guild_id)

        # キャッシュ済みのメンバーから取得する
        member = guild.get_member(user)

        # 見つからなければ再取得を試みる
        if member is None:
            try:
                member = await guild.fetch_member(user)
            except discord.HTTPException:
                return False

        # メンバーがいないとき
        if member is None:
            print(f"Error: 指定されたメンバー {user} が見つかりませんでした ({guild})")
            return False

        # ロールがないとき
        role_id = GiveRole.get(guild.id).role_id
        role = guild.get_role(role_id)
        if role is None:
            print(f"Error: 指定されたロール {config.ROLE_ID} が見つかりませんでした ({guild})")
            return False

        try:
            # ロールを追加する
            await member.add_roles(role)
            return True

        except (Exception,):
            traceback.print_exc()
            return False
