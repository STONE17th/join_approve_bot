from typing import List, Tuple, Any

import psycopg2
import os
from datetime import datetime

class DataBase:
    _instance = None
    db_path = 'database/sqlite3.db'
    _user_name = os.getenv('USER_NAME')
    _password = os.getenv('PASSWORD')
    _db_name = os.getenv('DB_NAME')
    _ip_address = os.getenv('IP_ADDRESS')

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # @staticmethod
    def execute(self, sql: str, parameters: tuple = tuple(),
                fetchone=False, fetchall=False, commit=False):
        connection = psycopg2.connect(
            user=self._user_name,
            password=self._password,
            dbname=self._db_name,
            host=self._ip_address,
        )
        db_cursor = connection.cursor()
        data = None
        db_cursor.execute(sql, parameters)
        if commit:
            connection.commit()
        if fetchone:
            data = db_cursor.fetchone()
        if fetchall:
            data = db_cursor.fetchall()
        connection.close()
        return data

    @staticmethod
    def _extract_kwargs(sql: str, parameters: dict, _and: bool = True) -> tuple:
        sql += (' AND ' if _and else ', ').join([f'{key} = ?' for key in parameters])
        return sql, tuple(parameters.values())

    def create_tables(self):
        sqls = ['''CREATE TABLE IF NOT EXISTS admins(
                entry_id        SERIAL PRIMARY KEY,
                channel_tg_id   NUMERIC,
                admin_tg_id     NUMERIC,
                min_requests    NUMERIC,
                max_requests    NUMERIC,
                UNIQUE (channel_tg_id, admin_tg_id)                
                )''',
                '''CREATE TABLE IF NOT EXISTS requests(
                entry_id        SERIAL PRIMARY KEY,
                channel_tg_id   NUMERIC,
                request_tg_id   NUMERIC,
                date_created    TIMESTAMP,
                UNIQUE (channel_tg_id, request_tg_id)
                )''',
                '''CREATE TABLE IF NOT EXISTS approved_requests(
                entry_id        SERIAL PRIMARY KEY,
                channel_tg_id   NUMERIC,
                request_tg_id   NUMERIC,
                date_approved   TIMESTAMP,
                UNIQUE (channel_tg_id, request_tg_id)
                )''',
                ]
        for sql in sqls:
            self.execute(sql, commit=True)

    def add_channel(self, channel_tg_id: int, admin_tg_id: int):
        sql = '''INSERT INTO admins(
                channel_tg_id,
                admin_tg_id)
                VALUES (%s, %s)
                '''
        self.execute(sql, (channel_tg_id, admin_tg_id), commit=True)

    def add_request(self, channel_tg_id: int, request_tg_id: int, date_created: datetime):
        sql = '''INSERT INTO requests(
                channel_tg_id,
                request_tg_id,
                date_created)
                VALUES (%s, %s, %s)
                '''
        self.execute(sql, (channel_tg_id, request_tg_id, date_created), commit=True)

    # def channel_length(self, channel_tg_id: int) -> int:
    #     sql = f'''SELECT count(*) FROM table_{channel_tg_id}'''
    #     return self.execute(sql, fetchall=True)

    def load_channels(self, admin_tg_id: int, all: bool = True) -> tuple[tuple[int], ...]:
        sql = '''SELECT channel_tg_id FROM admins WHERE admin_tg_id=%s'''
        return self.execute(sql, (admin_tg_id,), fetchall=True)

    def load_requests(self, channel_tg_id: int) -> list[tuple[Any, ...]] | tuple[Any, ...] | None:
        sql = '''SELECT request_tg_id FROM requests WHERE channel_tg_id=%s'''
        return self.execute(sql, (channel_tg_id,), fetchall=True)

    # def load_admin_channels(self, admin_tg_id: int):
    #     sql = '''SELECT channel_id, channel_tg_id FROM channels_admins WHERE admin_tg_id=%s'''
    #     return self.execute(sql, (admin_tg_id,), fetchall=True)
    #
    # def load_requests(self, channel_id: int):
    #     sql = 'SELECT entry_id, user_tg_id FROM users_join_requests WHERE channel_id=?'
    #     return self.execute(sql, (channel_id,), fetchall=True)

    # def _get_channel_id(self, channel_tg_id: int):
    #     sql = 'SELECT channel_id FROM channels_admins WHERE channel_tg_id=?'
    #     return int(self.execute(sql, (channel_tg_id,), fetchone=True)[0])

    # def add_join_request(self, channel_tg_id: int, user_id: int):
    #     channel_id = self._get_channel_id(channel_tg_id)
    #     sql = '''INSERT OR IGNORE INTO users_join_requests(
    #             channel_id,
    #             user_tg_id)
    #             VALUES (?, ?)
    #             '''
    #     self.execute(sql, (channel_id, user_id), commit=True)

    def delete_request(self, channel_tg_id: int, request_tg_id: int):
        sql = 'DELETE FROM requests WHERE channel_tg_id=%s AND request_tg_id=%s'
        self.execute(sql, (channel_tg_id, request_tg_id), commit=True)

    def delete_channel(self, channel_tg_id: int, admin_tg_id: int):
        sql = 'DELETE FROM admins WHERE channel_tg_id=%s AND admin_tg_id=%s'
        self.execute(sql, (channel_tg_id, admin_tg_id), commit=True)
