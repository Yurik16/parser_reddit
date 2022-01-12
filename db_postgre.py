import logging
from configparser import ConfigParser
from datetime import datetime

import psycopg2

from AbcDatabase import AbcDatabase


class PostgreDB(AbcDatabase):

    def __init__(self, filename='database.ini', section='postgresql'):
        self.db = {}
        self.filename = filename
        self.section = section
        self.parser = ConfigParser()
        self.parser.read(self.filename)
        if self.parser.has_section(self.section):
            self.params = self.parser.items(self.section)
            for param in self.params:
                self.db[param[0]] = param[1]
        else:
            raise Exception(f"Section {self.section} not found in the {self.filename} file")
        self.connection = psycopg2.connect(**self.db)
        self.cursor = self.connection.cursor()
        self.connection.autocommit = True
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS pg_users(
                user_id SERIAL PRIMARY KEY,
                user_name VARCHAR(50) NOT NULL,
                user_link VARCHAR(255) NOT NULL,
                total_karma INTEGER NOT NULL,
                comment_karma INTEGER NOT NULL,
                link_karma INTEGER NOT NULL,
                cake_day DATE NOT NULL);"""
        )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS pg_posts(
                post_uid VARCHAR PRIMARY KEY,
                author INTEGER NOT NULL,
                post_category VARCHAR(50) NOT NULL,
                post_date DATE NOT NULL,
                number_of_comments VARCHAR(10) NOT NULL,
                post_votes VARCHAR(10) NOT NULL,
                post_link VARCHAR(255) NOT NULL,
                FOREIGN KEY (author) 
                    REFERENCES pg_users (user_id)
                    ON UPDATE CASCADE ON DELETE CASCADE
                            );"""
        )
        self.logging_init()

    def config(self) -> dict:
        """Setting db connection parameters"""
        if self.parser.has_section(self.section):
            params = self.parser.items(self.section)
            for param in params:
                self.db[param[0]] = param[1]
        else:
            raise Exception(f"Section {self.section} not found in the {self.filename} file")
        return self.db

    @staticmethod
    def logging_init() -> None:
        """Init logging"""
        logging.basicConfig(filename="log.txt", filemode='a',
                            format='%(asctime)s :: %(levelname)s :: %(funcName)s :: %(lineno)d :: %(message)s',
                            level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")

    def connection_to_db(self) -> 'connection':
        """Connect to the suppliers db"""
        params = self.config()
        return psycopg2.connect(**params)

    def insert_user(self, user_name: str, user_link: str, total_karma: int, comment_karma: int, link_karma: int,
                    cake_day: str) -> None:
        """
        Insertion a new user into pg_users table
        :param user_name:
        :param user_link:
        :param total_karma:
        :param comment_karma:
        :param link_karma:
        :param cake_day:
        :return:
        """
        cmd = "INSERT INTO pg_users (user_name, user_link, total_karma, comment_karma, link_karma, cake_day) " \
              "VALUES (%s, %s, %s, %s, %s, %s)"
        is_duplicate = "SELECT count(*) FROM pg_users WHERE user_name LIKE %s"

        connection = self.connection_to_db()
        with connection:
            cursor = connection.cursor()
            cursor.execute(is_duplicate, (user_name,))
            count_of_duplicate = cursor.fetchone()
            if count_of_duplicate[0]:
                logging.warning("duplicates detected")
                return
            cursor.execute(cmd, (user_name, user_link, total_karma, comment_karma, link_karma, cake_day))

    def insert_post(self, uid: str, user_name: str, post_category: str, post_date: str, number_of_comments: str,
                    post_votes: str, post_link: str) -> None:
        """
        Insertion a new post into pg_posts table
        :param uid: unique id of post
        :param user_name: name of post author
        :param post_category:
        :param post_date:
        :param number_of_comments:
        :param post_votes:
        :param post_link:
        :return: None
        """
        cmd = "INSERT INTO pg_posts (" \
              "post_uid, author, post_category, post_date, number_of_comments, post_votes, post_link" \
              ") VALUES (%s, %s, %s, %s, %s, %s, %s)"
        # find the same post_link in db
        is_duplicate = "SELECT count(*) FROM pg_posts WHERE post_link LIKE %s"
        # find the user_name in db for getting user_id as author
        author_is = "SELECT user_id FROM pg_users WHERE user_name LIKE %s"

        connection = self.connection_to_db()
        with connection:
            cursor = connection.cursor()
            # if the same post_link exist in db - logging warning happens
            cursor.execute(is_duplicate, (post_link,))
            count_of_duplicate = cursor.fetchone()
            if count_of_duplicate[0]:
                logging.warning("duplicates detected")
                return
            try:
                # getting user_id as author or logging warning happens
                cursor.execute(author_is, (user_name,))
                user_id = cursor.fetchone()[0]
                cursor.execute(cmd, (uid, user_id, post_category, post_date, number_of_comments, post_votes, post_link))
            except TypeError as te:
                logging.warning(f'There is no "{user_name}" user at db')
            except Exception as e:
                logging.warning(f'{e}')

    def get_all_entry(self) -> list:
        """
        Get all data from DataBase
        :return: list of all post`s data
        """
        create_view = "CREATE OR REPLACE VIEW view_all AS SELECT " \
                      "p.post_uid, p.post_category, p.post_link, p.number_of_comments, p.post_votes, " \
                      "p.post_date, u.user_name, u.total_karma, u.comment_karma, u.cake_day " \
                      "FROM pg_posts as p JOIN pg_users as u " \
                      "ON p.author = u.user_id"
        cmd = "SELECT * FROM view_all"

        connection = self.connection_to_db()
        with connection:
            cursor = connection.cursor()
            cursor.execute(create_view)
            cursor.execute(cmd)
            result = cursor.fetchall()
            to_list = [', '.join(map(str, entry)) for entry in result]
            return to_list

    def get_one_entry(self, uid: str) -> str:
        """
        Get data of one post from DataBase
        :param uid: unique id of post
        :return: list of specific post`s data
        """
        cmd = "SELECT p.post_uid, p.post_category, p.post_link, p.number_of_comments, p.post_votes, " \
              "p.post_date, u.user_name, u.total_karma, u.comment_karma, u.link_karma, u.cake_day " \
              "FROM pg_posts as p JOIN pg_users as u " \
              "ON p.author = u.user_id " \
              "WHERE p.post_uid LIKE %s"
        connection = self.connection_to_db()
        with connection:
            cursor = connection.cursor()
            try:
                cursor.execute(cmd, (uid,))
                result = cursor.fetchone()
                result_as_str = ', '.join(map(str, result))
                return result_as_str
            except Exception as e:
                logging.warning(f'There is no such element in DB - {uid}: {e}')

    def delete_post(self, uid: str) -> None:
        """
        Delete entry from postgre DB
        :param uid: unique id of post
        """
        cmd = "DELETE FROM pg_posts WHERE post_uid LIKE %s"
        connection = self.connection_to_db()
        with connection:
            cursor = connection.cursor()
            try:
                cursor.execute(cmd, (uid,))
            except Exception as e:
                logging.warning(f'There is no such element in DB - {uid} : {e}')

    def update_post(self, uid: str, user_name: str, post_category: str, post_date: str, number_of_comments: str,
                    post_votes: str, post_link: str) -> None:
        """
        Update post in pg_posts
        :param uid: unique id of post
        :param user_name: user name
        :param post_category: new post_category
        :param post_date: new post_date
        :param number_of_comments: new number_of_comments
        :param post_votes: new post_votes
        :param post_link: new post_link
        :return: None
        """
        find_author = "select p.author from pg_posts as p join pg_users u on u.user_id = p.author " \
                      "where p.post_uid like %s"
        cmd = f"UPDATE pg_posts SET author=%s, post_category='{post_category}', post_date='{post_date}', " \
              f"number_of_comments='{number_of_comments}', post_votes='{post_votes}',  post_link='{post_link}'" \
              f"WHERE post_uid LIKE %s"
        connection = self.connection_to_db()
        with connection:
            cursor = connection.cursor()
            try:
                cursor.execute(find_author, (uid,))
                author = cursor.fetchone()
                cursor.execute(cmd, (author, uid,))
            except Exception as e:
                logging.warning(f'There is no such post_uid in DB - {uid}: {e}')

    def update_user(self, uid: str, user_name: str, user_link: str, total_karma: int, comment_karma: int,
                    link_karma: int, cake_day: str) -> None:
        """
        Update user in gp_users
        :param uid: unique id of post
        :param user_name: new user_name
        :param user_link: new user_link
        :param total_karma: new total_karma
        :param comment_karma: new comment_karma
        :param link_karma: new link_karma
        :param cake_day: new cake_day
        :return: None
        """
        # find the user_name in db using uid
        find_user_name = "SELECT user_name FROM pg_users WHERE user_id = %s"
        find_author = "SELECT author FROM pg_posts WHERE post_uid LIKE %s"

        cmd = f"UPDATE pg_users SET user_name='{user_name}', user_link='{user_link}',total_karma={total_karma}, " \
              f"link_karma={comment_karma}, comment_karma={comment_karma}, cake_day='{cake_day}'" \
              f"WHERE user_name LIKE %s"
        connection = self.connection_to_db()
        with connection:
            cursor = connection.cursor()
            try:
                cursor.execute(find_author, (uid,))
                author = cursor.fetchone()
                cursor.execute(find_user_name, author)
                old_user_name = cursor.fetchone()
                cursor.execute(cmd, (old_user_name,))
            except Exception as e:
                logging.warning(f'There is no such unique id of post in DB - {uid}: {e}')


if __name__ == '__main__':
    postgre_db = PostgreDB()
    #
    # postgre_db.insert_user('second_user', 'second_user_link', 2000, 200, 20, datetime(2021, 12, 12).strftime('%Y/%m/%d'))
    # postgre_db.insert_user('first_user', 'first_user_link', 1001, 101, 11, datetime(2011, 1, 1).strftime('%Y/%m/%d'))
    # postgre_db.insert_user('new_user', 'new_user_link', 3000, 300, 30, datetime(2020, 11, 11).strftime('%Y/%m/%d'))
    #
    # postgre_db.insert_post("df8aef88", "second_user", "post_category",datetime.now().strftime('%Y/%m/%d'), 22, 33, "post_link1")
    # postgre_db.insert_post("df7aef87", "new_user", "category", datetime.now().strftime('%Y/%m/%d'), 24, 32, "post_link2")
    # postgre_db.insert_post("df6aef86", "first_user", "post_category", datetime.now().strftime('%Y/%m/%d'), 22, 33, "post_link2")

    # print(postgre_db.get_all_entry())
    # new_entry = ['df6aef86', 3, 'category', 'link2', 111, 111, datetime.now().strftime('%Y/%m/%d')]
    # postgre_db.update_post('22222222-7240-11ec-af2b-b42e99d62b21', 51, 'SmileSmile', '2021-12-31', 500, 1500, '/r/gaming/comments/qvenew/LLLLLLLL/')
    # postgre_db.update_user('22222222-7240-11ec-af2b-b42e99d62b21', 'AAAAAAAA', '/user/AAAAAAAA/', 10000, 1000, 100, '2021-09-26')
    # # postgre_db.delete_post("df6aef86")
    # print(postgre_db.get_one_entry("df6aef86"))
