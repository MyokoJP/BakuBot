import sqlite3
from datetime import datetime
from typing import Union

from utils import Database


class GiveRole:
    def __init__(self, guild_id: int, role_id: int, created_at: datetime, updated_at: datetime):
        self.guild_id = guild_id
        self.role_id = role_id
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def set(guild_id: int, role_id: int):
        """
        ギルド設定にロールIDを追加(更新)します

        :param guild_id: ギルドID
        :param role_id: ロールID
        """

        conn = Database.get_connection()
        cur = conn.cursor()

        now = datetime.now().replace(microsecond=0)
        sql = "INSERT INTO guilds VALUES(?, ?, ?, ?) ON CONFLICT(guild_id) DO UPDATE SET role_id = excluded.role_id, updated_at = excluded.updated_at"
        cur.execute(sql, (guild_id, role_id, now, now))

        conn.commit()
        conn.close()

    @staticmethod
    def get(guild_id: int) -> Union['GiveRole', None]:
        """
        ギルドIDからGiveRole型を取得します

        :param guild_id: ギルドID
        :return: GiveRole型
        """

        conn = Database.get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        sql = "SELECT * FROM guilds WHERE guild_id = ?"
        cur.execute(sql, (guild_id,))

        result = cur.fetchone()
        if not result:
            return None

        return GiveRole(
            result["guild_id"],
            result["role_id"],
            datetime.strptime(result["created_at"],"%Y-%m-%d %H:%M:%S"),
            datetime.strptime(result["updated_at"], "%Y-%m-%d %H:%M:%S")
        )
