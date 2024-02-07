import sqlite3

import config


class Database:
    @staticmethod
    def initialize():
        """
        データベースを初期化します
        """

        conn = Database.get_connection()
        cur = conn.cursor()

        cur.execute("CREATE TABLE IF NOT EXISTS members(guild_id INTEGER, user_id INTEGER, verified_at TEXT, access_token TEXT, refresh_token TEXT, expires_at TEXT, PRIMARY KEY (guild_id, user_id))")
        cur.execute("CREATE TABLE IF NOT EXISTS guilds(guild_id INTEGER PRIMARY KEY, role_id INTEGER, created_at TEXT, updated_at TEXT)")
        conn.commit()
        conn.close()

    @staticmethod
    def get_connection():
        """
        コネクションを取得します

        :return: Connection
        """

        return sqlite3.connect(config.DATABASE_NAME)