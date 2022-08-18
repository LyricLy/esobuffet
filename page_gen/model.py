from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


engine = create_engine("sqlite:///db.sqlite3")
Base = declarative_base()
Session = sessionmaker(bind=engine)


def init_db(reset=False):
    if reset:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


class File(Base):
    __tablename__ = 'file'

    name = Column(String, primary_key=True)
    round = Column(Integer, primary_key=True)
    player = Column(String, primary_key=True)
    language = Column(String, default='plaintext')


class Round(Base):
    __tablename__ = 'round'

    id = Column(Integer, primary_key=True)
    start = Column(DateTime)
    first_deadline = Column(DateTime)
    second_deadline = Column(DateTime)


class Player(Base):
    __tablename__ = 'player'

    id = Column(Integer, primary_key=True)
    round = Column(Integer, primary_key=True)
    name = Column(String, primary_key=True)


class Solution(Base):
    __tablename__ = 'solution'

    round = Column(Integer, primary_key=True)
    player = Column(Integer, primary_key=True)
    solved = Column(Integer, primary_key=True)
