from sqlalchemy import Column, Integer, String, DateTime

from base import BaseModel


class RedditUser(BaseModel):
    __tablename__ = 'Users'

    user_name = Column(String)
    user_link = Column(String)
    total_carma = Column(Integer)
    commit_carma = Column(Integer)
    cake_day = Column(DateTime)

    def __repr__(self):
        return f'{self.user_name}'


class RedditPost(BaseModel):
    __tablename__ = 'Posts'
