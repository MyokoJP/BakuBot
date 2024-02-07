import logging
import sqlite3
from datetime import datetime, timedelta

import requests

import config
from utils import Database


class VerifiedMember:
    def __init__(self, user_id: int, verified_at: datetime, access_token: str, refresh_token: str, expires_at: datetime):
        self.user_id = user_id
        self.verified_at = verified_at
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at

    @staticmethod
    def add(guild_id: int, user_id: int, access_token: str, refresh_token: str, expires_in: int):
        """
        認証済みユーザーを追加します

        :param user_id: DiscordのユーザーID
        :param guild_id: ギルドID
        :param access_token: アクセストークン
        :param refresh_token: リフレッシュトークン
        :param expires_in: アクセストークンの有効期限(秒)
        """

        conn = Database.get_connection()
        cur = conn.cursor()

        now = datetime.now().replace(microsecond=0)
        expires_at = now + timedelta(seconds=expires_in)

        sql = "INSERT OR IGNORE INTO members VALUES(?, ?, ?, ?, ?, ?)"
        cur.execute(sql, (guild_id, user_id, str(now), access_token, refresh_token, str(expires_at)))

        conn.commit()
        conn.close()

    @staticmethod
    def get(guild_id: int):
        """
        DBに保存された認証済みユーザーをギルドIDから取得します
        :param guild_id: ギルドID

        :return: list[VerifiedMember]
        """

        conn = Database.get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        sql = "SELECT * FROM members WHERE guild_id = ?"
        cur.execute(sql, (guild_id,))

        result = cur.fetchall()
        return [VerifiedMember(
            i["user_id"],
            datetime.strptime(i["verified_at"], "%Y-%m-%d %H:%M:%S"),
            i["access_token"],
            i["refresh_token"],
            datetime.strptime(i["expires_at"], "%Y-%m-%d %H:%M:%S"),
        ) for i in result]

    @staticmethod
    def get_all():
        """
        DBに保存された認証済みユーザーをすべて取得します

        :return: list[VerifiedMember]
        """

        conn = Database.get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        sql = "SELECT * FROM members"
        cur.execute(sql)

        result = cur.fetchall()
        return [VerifiedMember(
            i["user_id"],
            datetime.strptime(i["verified_at"], "%Y-%m-%d %H:%M:%S"),
            i["access_token"],
            i["refresh_token"],
            datetime.strptime(i["expires_at"], "%Y-%m-%d %H:%M:%S"),
        ) for i in result]

    @staticmethod
    def refresh():
        """
        アクセストークンを再取得し、保存します
        """

        conn = Database.get_connection()
        cur = conn.cursor()

        members = VerifiedMember.get_all()
        now = datetime.now()
        for i in members:
            if now > i.expires_at:
                request_post = {
                    "grant_type": "refresh_token",
                    "refresh_token": i.refresh_token,
                    "client_id": config.CLIENT_ID,
                    "client_secret": config.CLIENT_SECRET,
                }
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded"
                }

                # access_tokenを取得
                request = requests.post("https://discord.com/api/oauth2/token",
                                        data=request_post, headers=headers)

                # StatusCodeが200でなかったらエラーを表示
                if request.status_code != 200:
                    logging.error(
                        f"access_tokenを取得できませんでした(Error: {request.json()}, RefreshToken: {i.refresh_token})"
                    )
                    continue

                # access_tokenを指定
                access_token = request.json()["access_token"]
                refresh_token = request.json()["refresh_token"]

                sql = "UPDATE members set access_token = ?, refresh_token = ? WHERE user_id = ?"
                cur.execute(sql, (access_token, refresh_token, i.user_id))
