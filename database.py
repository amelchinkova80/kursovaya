import logging as log
from os import name
import sqlite3


class Database:
    def __init__(self, db_path) -> None:
        self.db_path = db_path

    def is_user_in_db(self, username):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute('SELECT COUNT(*) FROM users WHERE login=?',
                        (username,))
            data = cur.fetchall()
            return data[0][0] != 0

    def add_user(self, username):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute('INSERT INTO users (login) VALUES (?)', (username,))
            con.commit()
            log.info(f'Added new user({username})')

    def add_user_category(self, username, category_id):
        user_id = self.get_user_id(username)

        user_category = self.get_user_categories(username)
        for _, id in user_category:
            if category_id == id:
                return False

        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute(
                'INSERT INTO user_categories (user_id, category_id) VALUES (?, ?)', (str(user_id), str(category_id)))
            con.commit()
            return True

    def remove_all_categories(self, username):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("""
                DELETE FROM user_categories WHERE user_id=(
                    SELECT id from users WHERE login=?)""", (username,))
            con.commit()

    def remove_user_info_provided(self, username):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("""DELETE FROM info_provided WHERE user_id=(
                SELECT id from users WHERE login=?)""", (username,))
            con.commit()

    def get_user_categories(self, username):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("""
                SELECT id, category_id FROM user_categories WHERE user_id=
                    (SELECT users.id FROM users WHERE users.login=?)""", (username,))
            data = cur.fetchall()
            return data

    def get_no_user_categories(self, username):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("""
                SELECT id, name FROM categories WHERE id NOT IN 
                (SELECT category_id FROM user_categories WHERE user_id=
                (SELECT users.id FROM users WHERE users.login=?))""", (username,))
            data = cur.fetchall()
            return data

    def get_all_categories(self):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute('SELECT * FROM categories')
            data = cur.fetchall()
            return data

    def get_user_id(self, username):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute('SELECT id FROM users WHERE login=?', (username,))
            data = cur.fetchall()
            return data[0][0]

    def get_info(self, info_id):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute(
                'SELECT title, description FROM info WHERE id=?', (info_id,))
            data = cur.fetchall()
            return data[0]

    def get_unprovided_info(self, username):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("""
                SELECT id
                FROM info
                WHERE id NOT IN (
                    SELECT info_id
                    FROM info_provided
                    WHERE user_id=(
                        SELECT id
                        FROM users
                        WHERE login=?
                    )
                )
            """, (username,))
            data = cur.fetchall()
            result = [d[0] for d in data]
            return result

    def get_provided_info(self, username):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("""
                SELECT id
                FROM info
                WHERE id IN (
                    SELECT info_id
                    FROM info_provided
                    WHERE user_id=(
                        SELECT id
                        FROM users
                        WHERE login=?
                    )
                )
            """, (username,))
            data = cur.fetchall()
            result = [d[0] for d in data]
            return result

    def get_similarity_categories(self, username, info_id):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("""
                SELECT COUNT(*)
                FROM info_categories
                WHERE category_id IN (
                    SELECT category_id 
                    FROM user_categories
                    WHERE user_id=(
                        SELECT id FROM users WHERE login=?
                    )
                ) AND info_id=?
            """, (username, info_id))
            data = cur.fetchall()
            return data[0][0]

    def get_all_info(self):
        result = []

        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute('SELECT id, title FROM info')
            data = cur.fetchall()

            for idx, name in data:
                cur.execute(
                    'SELECT name FROM categories WHERE id IN (SELECT category_id FROM info_categories WHERE category_id=?)', (idx,))
                tegs = cur.fetchall()
                _tegs = [t[0] for t in tegs]
                result.append((idx, name, _tegs))

        return result

    def get_info_for_admin(self, info_id):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute('SELECT * FROM info WHERE id=?', (info_id,))
            data = cur.fetchall()
            return data[0]

    def get_category_for_admin(self, category_id):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute('SELECT * FROM categories WHERE id=?', (category_id,))
            data = cur.fetchall()
            return data[0]

    def remove_info(self, info_id):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute('DELETE FROM info WHERE id=?', (info_id,))
            con.commit()

    def remove_category(self, category_id):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute('DELETE FROM categories WHERE id=?', (category_id,))
            con.commit()

    def add_info(self, title, desc):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute(
                'INSERT OR REPLACE INTO info (title, description) VALUES (?, ?)', (title, desc,))
            con.commit()

    def add_category_to_info(self, info_id, category_id):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute(
                'INSERT INTO tegs (info_id, category_id) VALUES (?, ?)', (info_id, category_id,))
            con.commit()

    def reset_categories_of_info(self, info_id):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute(
                'DELETE FROM info_categories WHERE info_id=?', (info_id,))
            con.commit()

    def add_category(self, name):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute(
                'INSERT OR REPLACE INTO categories (name) VALUES (?)', (name,))
            con.commit()

    def insert_provided_info(self, username, info_id):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("""
                INSERT INTO info_provided (info_id, user_id) VALUES 
                (?, (SELECT id FROM users u WHERE u.login=?))
                """, (info_id, username,))
            con.commit()
