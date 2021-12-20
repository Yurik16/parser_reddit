import json
from datetime import datetime

import psycopg2

from pg_connect import config


class UserTable:

    def __init__(self):
        self.user_id = 'user_id'
        self.user_name = 'user_name'
        self.total_carma = 'total_carma'
        self.comment_carma = 'comment_carma'
        self.cake_day = 'cake_day'


def create_table_users():
    """Create table users in the PostgreSQL database"""
    command = """
    CREATE TABLE pg_users (
        user_id SERIAL PRIMARY KEY,
        user_name VARCHAR(50) NOT NULL,
        total_carma INTEGER NOT NULL,
        comment_carma INTEGER NOT NULL,
        cake_day DATE NOT NULL);
        """
    conn = None
    params = config()
    conn = psycopg2.connect(**params)
    with conn:
        cur = conn.cursor()
        try:
            cur.execute(command)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)


def create_table_posts():
    """Create table pg_posts in the PostgreSQL database"""
    command = """
    CREATE TABLE pg_posts (
        post_uid VARCHAR PRIMARY KEY,
        author INTEGER NOT NULL,
        post_category VARCHAR(50) NOT NULL,
        post_link VARCHAR NOT NULL,
        number_of_comments INTEGER NOT NULL,
        post_votes INTEGER NOT NULL,
        post_date DATE NOT NULL,
        FOREIGN KEY (author) 
            REFERENCES pg_users (user_id)
            ON UPDATE CASCADE ON DELETE CASCADE
            )
        """
    conn = None
    params = config()
    conn = psycopg2.connect(**params)
    with conn:
        cur = conn.cursor()
        try:
            cur.execute(command)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)


def insert_user(user_name: str, total_carma: int, comment_carma: int, cake_day: datetime):
    """Insertion a new user into pg_users table"""
    cmd = "INSERT INTO pg_users (user_name, total_carma, comment_carma, cake_day) VALUES (%s, %s, %s, %s)"
    is_duplicate = "SELECT count(*) FROM pg_users WHERE user_name LIKE %s"

    params = config()
    connection = psycopg2.connect(**params)
    with connection:
        cursor = connection.cursor()
        cursor.execute(is_duplicate, (user_name,))
        count_of_duplicate = cursor.fetchone()
        if count_of_duplicate[0]:
            print("duplicates detected")
            return
        cursor.execute(cmd, (user_name, total_carma, comment_carma, cake_day))


def insert_post(uid: str, author: str, post_category: str, post_link: str, number_of_comments: int, post_votes: int,
                post_date: datetime):
    """Insertion a new post into pg_posts table"""
    cmd = "INSERT INTO pg_posts (" \
          "post_uid, author, post_category, post_link, number_of_comments, post_votes, post_date" \
          ") VALUES (%s, %s, %s, %s, %s, %s, %s)"
    is_duplicate = "SELECT count(*) FROM pg_posts WHERE post_link LIKE %s"
    user_id_is = "SELECT user_id FROM pg_users WHERE user_name LIKE %s"

    params = config()
    connection = psycopg2.connect(**params)
    with connection:
        cursor = connection.cursor()
        cursor.execute(is_duplicate, (post_link,))
        count_of_duplicate = cursor.fetchone()
        if count_of_duplicate[0]:
            print("duplicates detected")
            return
        try:
            cursor.execute(user_id_is, (author,))
            user_id = cursor.fetchone()[0]
            cursor.execute(cmd, (uid, user_id, post_category, post_link, number_of_comments, post_votes, post_date))
        except TypeError as te:
            print(f'There is no "{author}" user at db')
        except Exception as e:
            print(e)


def get_all_entry() -> str:
    """Get all data from db"""
    cmd = "SELECT * FROM pg_posts as p JOIN pg_users as u" \
          " ON p.author = u.user_id"
    params = config()
    connection = psycopg2.connect(**params)
    with connection:
        cursor = connection.cursor()
        cursor.execute(cmd)
        result = cursor.fetchall()
        to_list = [[f'{elem}' for elem in entry] for entry in result]
        return json.dumps(to_list)


def get_one_entry(id: int) -> str:
    cmd = "SELECT * FROM pg_posts as p JOIN pg_users as u" \
          " ON p.author = u.user_id WHERE "
    params = config()
    connection = psycopg2.connect(**params)
    with connection:
        cursor = connection.cursor()
        cursor.execute(cmd)
        result = cursor.fetchall()
        to_list = [[f'{elem}' for elem in entry] for entry in result]
        return json.dumps(to_list)


create_table_posts()
create_table_users()
insert_user('second_user', 2000, 20, datetime(2021, 12, 12).strftime('%Y/%m/%d'))
insert_user('new_user', 3000, 30, datetime(2020, 11, 11).strftime('%Y/%m/%d'))
insert_post("df8aef88", "second_user", "post_category", "post_link1", 22, 33, datetime.now().strftime('%Y/%m/%d'))
insert_post("df7aef87", "new_user", "category", "post_link4", 24, 32, datetime.now().strftime('%Y/%m/%d'))
insert_post("df6aef86", "first_user", "post_category", "post_link2", 22, 33, datetime.now().strftime('%Y/%m/%d'))
print(get_all_entry())
