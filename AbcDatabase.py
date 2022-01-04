from abc import ABC, abstractmethod


class AbcDatabase(ABC):
    @abstractmethod
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

    @abstractmethod
    def insert_post(self, uid: str, author: str, post_category: str, post_date: str, number_of_comments: str,
                    post_votes: str, post_link: str) -> None:
        """
        Insertion a new post into pg_posts table
        :param uid: unique id of post
        :param author: name of post author
        :param post_category:
        :param post_date:
        :param number_of_comments:
        :param post_votes:
        :param post_link:
        :return: None
        """

    @abstractmethod
    def get_all_entry(self) -> list:
        """
        Get all data from DataBase
        :return: list of all post`s data
        """

    @abstractmethod
    def get_one_entry(self, uid: str) -> list:
        """
        Get data of one post from DataBase
        :param uid: unique id of post
        :return: list of specific post`s data
        """

    @abstractmethod
    def delete_post(self, uid: str) -> None:
        """
        Delete entry from DataBase
        :param uid: unique id of post
        :return: None
        """

    def update_user(self, old_u_name: str, user_name: str, user_link: str, total_karma: int, comment_karma: int,
                    cake_day: str) -> None:
        """
        Update user in gp_users
        :param old_u_name: user name searching for update
        :param user_name: new user_name
        :param user_link: new user_link
        :param total_karma: new total_karma
        :param comment_karma: new comment_karma
        :param cake_day: new cake_day
        :return: None
        """

    @abstractmethod
    def update_post(self, uid: str, author: str, post_category: str, post_date: str, number_of_comments: str,
                    post_votes: str, post_link: str) -> None:
        """
        Update post in pg_posts
        :param uid:
        :param author:
        :param post_category:
        :param post_date:
        :param number_of_comments:
        :param post_votes:
        :param post_link:
        :return:
        """
