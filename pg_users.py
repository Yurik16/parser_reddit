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
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(command)
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def insert_user(user_name: str, total_carma: int, comment_carma: int, cake_day: datetime):
    """Insertion a new user into users table"""
    cmd = "INSERT INTO pg_users (user_name, total_carma, comment_carma, cake_day) VALUES (%s, %s, %s, %s)"

    params = config()
    connection = psycopg2.connect(**params)
    with connection:
        cursor = connection.cursor()
        cursor.execute(cmd, (user_name, total_carma, comment_carma, cake_day))


create_table_users()
insert_user('first_user', 1000, 10, datetime(12, 12, 12))
