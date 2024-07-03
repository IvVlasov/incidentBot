import sqlite3
from settings import DB_PATH, CLAIM_LENGTH
import random


connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()


def _get(param):
    if param is None:
        return ''
    return param


def init_db():
    # Создаем таблицу Users
    sql = '''CREATE TABLE IF NOT EXISTS users (
            chat_id BIGINT PRIMARY KEY,
            username TEXT DEFAULT NULL,
            full_name TEXT DEFAULT NULL,
            phone_number TEXT DEFAULT NULL)'''
    cursor.execute(sql)

    sql = '''CREATE TABLE IF NOT EXISTS claim_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL UNIQUE)'''
    cursor.execute(sql)
    ClaimTypes.init_data()

    sql = '''CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id INTEGER,
            file_id TEXT NOT NULL,
            file_type TEXT NOT NULL,
            FOREIGN KEY (claim_id)  REFERENCES claims (record_id))'''
    cursor.execute(sql)

    sql = '''CREATE TABLE IF NOT EXISTS claims (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id BIGINT,
            type TEXT,
            descr TEXT,
            contact TEXT DEFAULT NULL,
            date datetime default current_timestamp,
            FOREIGN KEY (user_id)  REFERENCES users (chat_id))'''
    cursor.execute(sql)


class Claim:

    @classmethod
    def create(cls, chat_id, data: dict):
        sql = '''insert into claims (record_id, user_id, type, descr, contact) values (?, ?, ?, ?, ?)'''
        record_id = cls._new_record_id()
        cursor.execute(
            sql,
            (record_id, chat_id, data['type'], data['descr'], data.get('contact', '-'))
        )
        connection.commit()
        return record_id

    @staticmethod
    def get(record_id):
        query = 'select * from claims where record_id = ?'
        cursor.execute(query, (record_id, ))
        rows = cursor.fetchone()
        return rows

    @classmethod
    def _new_record_id(cls):
        n = ''
        for _ in range(CLAIM_LENGTH):
            n += str(random.randint(1, 9))
        exist = cls.get(n)
        if exist:
            return int(cls._new_record_id())
        return int(n)

    @staticmethod
    def get_full_claim(record_id):
        query = '''select * from claims join users on users.chat_id = claims.user_id where record_id = ?'''
        cursor.execute(query, (record_id, ))
        rows = cursor.fetchone()
        return rows


class Files:

    @staticmethod
    def add(file_list, record_id):
        sql = '''insert or ignore into files (claim_id, file_id, file_type) values (?, ?, ?)'''
        for el in file_list:
            cursor.execute(sql, (record_id, el['file_id'], el['file_type']))
        connection.commit()

    @staticmethod
    def get(record_id):
        sql = '''select * from files where claim_id = ?'''
        cursor.execute(sql, (record_id, ))
        rows = cursor.fetchall()
        return rows


class ClaimTypes:

    def init_data():
        sql = '''insert or  ignore into claim_types (id, text) values (300, ?)'''
        cursor.execute(sql, ('Другое', ))
        connection.commit()

    @classmethod
    def get_all(cls):
        query = 'select * from claim_types'
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows

    @classmethod
    def add(cls, text):
        sql = '''insert or ignore into claim_types (text) values (?)'''
        cursor.execute(sql, (text, ))
        connection.commit()

    @classmethod
    def delete(cls, ident):
        sql = '''delete from claim_types where id = ?'''
        cursor.execute(sql, (ident, ))
        connection.commit()


class User:
    def __init__(self, chat):
        self.chat = chat

    def get_user(self):
        query = 'select * from users where chat_id = ?'
        cursor.execute(query, (self.chat.id, ))
        user = cursor.fetchone()
        return user

    def create_user(self):
        sql = 'insert or ignore into users (chat_id, username, full_name) values (?, ?, ?)'
        full_name = self._fullname()
        username = _get(self.chat.username)
        cursor.execute(sql, (self.chat.id, username, full_name))
        connection.commit()

    def _fullname(self):
        return _get(self.chat.first_name) + _get(self.chat.last_name)

    def update_phone(self, phone_number):
        sql = 'update users set phone_number=? where chat_id=?'
        cursor.execute(sql, (phone_number, self.chat.id))
        connection.commit()

    @classmethod
    def get_user_by_id(cls, chat_id):
        query = 'select * from users where chat_id = ?'
        cursor.execute(query, (chat_id, ))
        user = cursor.fetchone()
        return user
