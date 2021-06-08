from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# FOR MYSQL
# pip install mysql-connector-python
# mysql+mysqlconnector://<user>:<password>@<host>[:<port>]/<dbname>
#                              connector_to_use  user pass     host      database
# engine = create_engine('mysql+mysqlconnector://user:password@localhost/<dbname>')
# Base = declarative_base(bind=engine)
# Session = orm.sessionmaker(bind=engine)


# create a engine to execute queries
# for a file, use sqlite:///file.sqlite instead of sqlite:///:memory:
engine = create_engine('sqlite:///:memory:')
# super class base for all table models
Base = declarative_base(bind=engine)
# session generator
Session = sessionmaker(bind=engine)


@contextmanager
def transaction():
    s = scoped_session(Session)
    try:
        yield s
        s.commit()
    except Exception as e:
        s.rollback()
        raise
    finally:
        s.close()


class User(Base):
    __tablename__ = 'users'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String, nullable=False)
    email: str = Column(String, nullable=False)

    # for convenience
    @classmethod
    def create(cls, name, email):
        return cls(name=name, email=email)

    def __repr__(self):
        return f'<{self.__class__.__name__} name={self.name} email={self.email}>'


Base.metadata.create_all()

with transaction() as conn:
    conn.add(User.create('jane', 'jane@doe.com'))
    conn.add(User.create('john', 'john@doe.com'))

with transaction() as conn:
    print(conn.query(User).all())
