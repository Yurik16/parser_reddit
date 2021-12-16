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
        post_id INTEGER PRIMARY KEY,
        post_category VARCHAR(50) NOT NULL,
        post_link VARCHAR NOT NULL,
        number_of_comments INTEGER NOT NULL,
        post_votes INTEGER NOT NULL,
        post_date DATE NOT NULL,
        FOREIGN KEY (post_id) 
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
    """Insertion a new user into users table"""
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


create_table_posts()
create_table_users()
insert_user('second_user', 2000, 20, datetime(2021, 12, 12))
