import sqlite3
import logging

logger = logging.getLogger(__name__)

class PersistentGuildStore:
    """
    Provides a persistent store of data for use in various Cogs.

    The persistent store provides cog-specific storage via key value
    pairs.
    """
    def __init__(self, guild_id: int, dbpath: str):
        self.__dbpath = dbpath
        self.__guild_id = guild_id

        with sqlite3.connect(self.__dbpath) as conn:
            cursor = conn.execute("PRAGMA USER_VERSION")

            if cursor.fetchone()[0] == 0:
                logger.info(f"initializing persistent storage at {dbpath}")
                cursor.execute("CREATE TABLE storage (guild_id INTEGER, key TEXT, value TEXT, PRIMARY KEY (guild_id, key))")
                cursor.execute("PRAGMA USER_VERSION=1")
                cursor.close()
                logger.info(f"successfully initialized persistent storage at {dbpath}")

    def get_value(self, key: str, default: str | None = None) -> str | None:
        with sqlite3.connect(self.__dbpath) as conn:
            cursor = conn.execute("SELECT value FROM storage WHERE guild_id=? AND key=?", (self.__guild_id, key,))
            row = cursor.fetchone()
            if row == None:
                return default
            else:
                return row[0]

    def set_value(self, key: str, value: str):
        with sqlite3.connect(self.__dbpath) as conn:
            conn.execute("INSERT INTO storage (guild_id, key, value) VALUES(?, ?, ?) ON CONFLICT(guild_id, key) DO UPDATE SET value=?",
                        (self.__guild_id, key, value, value))

    def delete_value(self, key: str):
        with sqlite3.connect(self.__dbpath) as conn:
            conn.execute("DELETE FROM storage WHERE guild_id=? AND key=?", (self.__guild_id, key,))

    def get_keys(self, prefix: str | None = None):
        with sqlite3.connect(self.__dbpath) as conn:
            if prefix:
                filter=f"{prefix}%"
                cursor = conn.execute("SELECT key FROM storage WHERE guild_id=? AND key LIKE ? ORDER BY KEY ASC", (self.__guild_id, filter))
            else:
                cursor = conn.execute("SELECT key FROM storage WHERE guild_id=? ORDER BY KEY ASC", (self.__guild_id,))

            result = []
            for row in cursor:
                result.append(row[0])

            return result