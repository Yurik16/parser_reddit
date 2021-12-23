import json
import pprint
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


def insert_user(user_name: str, total_carma: int, comment_carma: int, cake_day: str):
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
                post_date: str):
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


def get_all_entry() -> list:
    """Get all data from postgre DB"""
    create_view = "CREATE OR REPLACE VIEW view_all AS SELECT " \
                  "p.post_uid, p.post_category, p.post_link, p.number_of_comments, p.post_votes, " \
                  "p.post_date, u.user_name, u.total_carma, u.comment_carma, u.cake_day " \
                  "FROM pg_posts as p JOIN pg_users as u " \
                  "ON p.author = u.user_id"
    cmd = "SELECT * FROM view_all"

    params = config()
    connection = psycopg2.connect(**params)
    with connection:
        cursor = connection.cursor()
        cursor.execute(create_view)
        cursor.execute(cmd)
        result = cursor.fetchall()
        to_list = [[f'{elem}' for elem in entry] for entry in result]
        return to_list


def get_one_entry(uid: str) -> list:
    """Get certain data from postgre DB"""
    cmd = "SELECT p.post_uid, p.post_category, p.post_link, p.number_of_comments, p.post_votes, " \
          "p.post_date, u.user_name, u.total_carma, u.comment_carma, u.cake_day " \
          "FROM pg_posts as p JOIN pg_users as u " \
          "ON p.author = u.user_id " \
          "WHERE p.post_uid LIKE %s"
    params = config()
    connection = psycopg2.connect(**params)
    with connection:
        cursor = connection.cursor()
        try:
            cursor.execute(cmd, (uid,))
            result = cursor.fetchone()
            to_list = [f'{elem}' for elem in result]
            return to_list
        except Exception as e:
            print(f'There is no such element in DB - {uid} ' + str(e))


def delete_post(uid: str):
    """Delete entry from postgre DB"""
    cmd = "DELETE FROM pg_posts WHERE post_uid LIKE %s"
    params = config()
    connection = psycopg2.connect(**params)
    with connection:
        cursor = connection.cursor()
        try:
            cursor.execute(cmd, (uid,))
        except Exception as e:
            print(f'There is no such element in DB - {uid} ' + str(e))


def update_post(uid: str, val: list):
    """Update post in pg_posts"""
    i_gen = (item for item in val)
    cmd = f"UPDATE pg_posts SET post_uid='{next(i_gen)}', author={next(i_gen)}, post_category='{next(i_gen)}', " \
          f"post_link='{next(i_gen)}', number_of_comments={next(i_gen)}, " \
          f"post_votes={next(i_gen)}, post_date='{next(i_gen)}'" \
          f"WHERE post_uid LIKE %s"
    params = config()
    connection = psycopg2.connect(**params)
    with connection:
        cursor = connection.cursor()
        try:
            cursor.execute(cmd, (uid,))
        except Exception as e:
            print(f'There is no such post_uid in DB - {uid} ' + str(e))


def update_user(user: str, val: list):
    """Update user in gp_users"""
    i_gen = (item for item in val)
    cmd = f"UPDATE pg_users SET user_name='{next(i_gen)}', total_carma={next(i_gen)}, " \
          f"comment_carma={next(i_gen)}, cake_day='{next(i_gen)}'" \
          f"WHERE user_name LIKE %s"
    params = config()
    connection = psycopg2.connect(**params)
    with connection:
        cursor = connection.cursor()
        try:
            cursor.execute(cmd, (user,))
        except Exception as e:
            print(f'There is no such user_name in DB - {user} ' + str(e))


create_table_posts()
create_table_users()
insert_user('second_user', 2000, 20, datetime(2021, 12, 12).strftime('%Y/%m/%d'))
insert_user('first_user', 1001, 11, datetime(2011, 1, 1).strftime('%Y/%m/%d'))
insert_user('new_user', 3000, 30, datetime(2020, 11, 11).strftime('%Y/%m/%d'))
insert_post("df8aef88", "second_user", "post_category", "post_link1", 22, 33, datetime.now().strftime('%Y/%m/%d'))
insert_post("df7aef87", "new_user", "category", "post_link4", 24, 32, datetime.now().strftime('%Y/%m/%d'))
insert_post("df6aef86", "first_user", "post_category", "post_link2", 22, 33, datetime.now().strftime('%Y/%m/%d'))

print(get_all_entry())
new_entry = ['df6aef86', 3, 'category', 'link2', 111, 111, datetime.now().strftime('%Y/%m/%d')]
# update_post('df6aef86', new_entry)
# delete_post("df6aef86")
print(get_one_entry("df6aef86"))
