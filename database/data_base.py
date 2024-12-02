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

    @classmethod
    def execute(cls, sql: str | list, parameters: tuple = tuple(),
                fetchone=False, fetchall=False, commit=False):
        connection = psycopg2.connect(
            user=cls._user_name,
            password=cls._password,
            dbname=cls._db_name,
            host=cls._ip_address,
        )
        db_cursor = connection.cursor()
        data = None
        if isinstance(sql, str):
            sql = [sql]
        for request in sql:
            db_cursor.execute(request, parameters)
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
                admin_tg_id     INTEGER,
                channel_tg_id   INTEGER,
                channel_title   CHARACTER VARYING(500),
                min_requests    INTEGER,
                max_requests    INTEGER,
                UNIQUE (channel_tg_id, admin_tg_id)                
                )''',
                '''CREATE TABLE IF NOT EXISTS requests(
                entry_id        SERIAL PRIMARY KEY,
                channel_tg_id   INTEGER,
                request_tg_id   INTEGER,
                creation_date   TIMESTAMP,
                UNIQUE (channel_tg_id, request_tg_id)
                )''',
                '''CREATE TABLE IF NOT EXISTS approved_requests(
                entry_id        SERIAL PRIMARY KEY,
                channel_tg_id   INTEGER,
                request_tg_id   INTEGER,
                approve_date    TIMESTAMP,
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

    @classmethod
    def refresh_channels(cls, channel_title: str, admin_tg_id: int, channel_tg_id: int):
        sql = '''UPDATE admins SET channel_title=%s WHERE admin_tg_id=%s AND channel_tg_id=%s'''
        return cls.execute(sql, (channel_title, admin_tg_id, channel_tg_id), commit=True)

    @classmethod
    def add_request(cls, channel_tg_id: int, request_tg_id: int, date_created: datetime):
        sql = '''INSERT INTO requests(
                channel_tg_id,
                request_tg_id,
                date_created)
                VALUES (%s, %s, %s)
                '''
        cls.execute(sql, (channel_tg_id, request_tg_id, date_created), commit=True)

    @classmethod
    def get_channel(cls, admin_tg_id: int, channel_tg_id) -> list[tuple[Any, ...]] | tuple[Any, ...] | None:
        sql = '''SELECT
                admin_tg_id,
                channel_tg_id,
                channel_title,
                min_requests,
                max_requests
                FROM admins WHERE admin_tg_id=%s AND channel_tg_id=%s'''
        return cls.execute(sql, (admin_tg_id, channel_tg_id), fetchone=True)

    def get_channels(self, admin_tg_id: int) -> tuple[tuple[int], ...]:
        sql = '''SELECT
                admin_tg_id,
                channel_tg_id,
                channel_title,
                min_requests,
                max_requests
                FROM admins WHERE admin_tg_id=%s'''
        return self.execute(sql, (admin_tg_id,), fetchall=True)

    @classmethod
    def load_requests(cls, channel_tg_id: int) -> list[tuple[Any, ...]] | tuple[Any, ...] | None:
        sql = '''SELECT request_tg_id, date_created FROM requests WHERE channel_tg_id=%s'''
        return cls.execute(sql, (channel_tg_id,), fetchall=True)

    def get_admin_limits(self, admin_tg_id: int, channel_tg_id: int):
        sql = '''SELECT min_requests, max_requests FROM admins WHERE admin_tg_id=%s AND channel_tg_id=%s'''
        return self.execute(sql, (admin_tg_id, channel_tg_id), fetchone=True)

    @classmethod
    def set_admin_limits(cls, admin_tg_id: int, channel_tg_id: int, min_value: int, max_value: int):
        sql = '''UPDATE admins SET min_requests=%s, max_requests=%s WHERE admin_tg_id=%s AND channel_tg_id=%s'''
        return cls.execute(sql, (min_value, max_value, admin_tg_id, channel_tg_id), commit=True)

    def delete_channel(self, channel_tg_id: int, admin_tg_id: int):
        sql = 'DELETE FROM admins WHERE channel_tg_id=%s AND admin_tg_id=%s'
        self.execute(sql, (channel_tg_id, admin_tg_id), commit=True)

    @classmethod
    def delete_request(cls, channel_tg_id: int, request_tg_id: int):
        sql = 'DELETE FROM requests WHERE channel_tg_id=%s AND request_tg_id=%s'
        cls.execute(sql, (channel_tg_id, request_tg_id), commit=True)
