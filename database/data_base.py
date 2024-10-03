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

    def load_join_requests(self, channel_tg_id: int):
        channel_id = self._get_channel_id(channel_tg_id)
        sql = 'SELECT entry_id, user_tg_id FROM users_join_requests WHERE channel_id=?'
        result = self.execute(sql, (channel_id,), fetchall=True)
        return list(map(lambda x: x[1], sorted(result)))

    def load_amount_requests_by_user(self, user_id: int):
        sql = '''SELECT channel_tg_id, user_tg_id FROM users_join_requests
                JOIN channels_admins ON users_join_requests.channel_id = channels_admins.channel_id
                WHERE admin_tg_id=?'''
        return self.execute(sql, (user_id,), fetchall=True)

    def load_admin_channels(self, admin_tg_id: int):
        sql = '''SELECT channel_tg_id FROM channels_admins WHERE admin_tg_id=?'''
        return list(map(lambda x: x[0], self.execute(sql, (admin_tg_id,), fetchall=True)))

    def delete_join_request(self, channel_tg_id: int, user_id: int):
        channel_id = self._get_channel_id(channel_tg_id)
        sql = 'DELETE FROM users_join_requests WHERE channel_id=? AND user_tg_id=?'
        self.execute(sql, (channel_id, user_id), commit=True)

    #
    # def new_user(self, user: list):
    #     sql = '''INSERT OR IGNORE INTO users(
    #             tg_id,
    #             username,
    #             first_name,
    #             last_name,
    #             balance,
    #             reg_date,
    #             status,
    #             options)
    #             VALUES (?, ?, ?)
    #             '''
    #     self.execute(sql, (*user,), commit=True)
    #
    # def load_bots(self):
    #     sql = '''SELECT token FROM bots'''
    #     return self.execute(sql, fetchall=True)
    #
    # def add_channel_to_bot(self, bot_id: int, channel_id: int):
    #     sql = '''UPDATE bots SET channel_tg_id=? WHERE tg_id=?'''
    #     self.execute(sql, (channel_id, bot_id), commit=True)
    #
    # def set_options(self, bot_id: int, option: str, value: int):
    #     sql = f'''UPDATE bots SET {option}=? WHERE tg_id=?'''
    #     self.execute(sql, (value, bot_id), commit=True)
    #
    # def toggle_auto_approve(self, bot_id: int):
    #     sql = 'SELECT auto_approve FROM bots WHERE tg_id=?'
    #     result = self.execute(sql, (bot_id,), fetchone=True)
    #     result = 0 if result[0] else 1
    #     sql = 'UPDATE bots SET auto_approve=? WHERE tg_id=?'
    #     self.execute(sql, (result, bot_id), commit=True)
    #     return result
