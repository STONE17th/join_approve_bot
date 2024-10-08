import sqlite3


class DataBase:
    _instance = None
    db_path = 'database/sqlite3.db'

    def __new__(cls):
        if not isinstance(cls._instance, cls):
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def execute(sql: str, parameters: tuple = tuple(),
                fetchone=False, fetchall=False, commit=False):
        connection = sqlite3.connect(DataBase.db_path)
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)
        if commit:
            connection.commit()
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data = cursor.fetchall()
        connection.close()
        return data

    @staticmethod
    def extract_kwargs(sql: str, parameters: dict, _and: bool = True) -> tuple:
        sql += (' AND ' if _and else ', ').join([f'{key} = ?' for key in parameters])
        return sql, tuple(parameters.values())

    def create_tables(self):
        sql_admins = '''CREATE TABLE IF NOT EXISTS channels_admins(
                channel_id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_tg_id INTEGER,
                channel_tg_id INTEGER,
                UNIQUE(admin_tg_id, channel_tg_id))
                '''
        sql_users = '''CREATE TABLE IF NOT EXISTS users_join_requests(
                entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER,
                user_tg_id INTEGER,
                UNIQUE(channel_id, user_tg_id),
                FOREIGN KEY (channel_id)  REFERENCES channels_admins (channel_id))
                '''

        for sql in (sql_admins, sql_users):
            self.execute(sql, commit=True)

    def add_new_channel(self, user_tg_id: int, channel_tg_id: int):
        sql = '''INSERT OR IGNORE INTO channels_admins(
                admin_tg_id,
                channel_tg_id)
                VALUES (?, ?)
                '''
        self.execute(sql, (user_tg_id, channel_tg_id), commit=True)

    def load_channel(self, tg_id: int):
        sql = '''SELECT channel_id, admin_tg_id FROM channels_admins WHERE channel_tg_id=?'''
        return self.execute(sql, (tg_id,), fetchone=True)

    def load_channels(self, admin_tg_id: int):
        sql = '''SELECT channel_id, channel_tg_id FROM channels_admins WHERE admin_tg_id=?'''
        return self.execute(sql, (admin_tg_id,), fetchall=True)

    def load_requests(self, channel_id: int):
        sql = 'SELECT entry_id, user_tg_id FROM users_join_requests WHERE channel_id=?'
        return self.execute(sql, (channel_id,), fetchall=True)

    def _get_channel_id(self, channel_tg_id: int):
        sql = 'SELECT channel_id FROM channels_admins WHERE channel_tg_id=?'
        return int(self.execute(sql, (channel_tg_id,), fetchone=True)[0])

    def add_join_request(self, channel_tg_id: int, user_id: int):
        channel_id = self._get_channel_id(channel_tg_id)
        sql = '''INSERT OR IGNORE INTO users_join_requests(
                channel_id,
                user_tg_id)
                VALUES (?, ?)
                '''
        self.execute(sql, (channel_id, user_id), commit=True)

    def delete_join_request(self, channel_id: int, user_tg_id: int):
        sql = 'DELETE FROM users_join_requests WHERE channel_id=? AND user_tg_id=?'
        self.execute(sql, (channel_id, user_tg_id), commit=True)
