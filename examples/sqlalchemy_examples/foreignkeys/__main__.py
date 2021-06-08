"""start of requirements"""
from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship

engine = create_engine('sqlite:///:memory:')
Base = declarative_base(bind=engine)
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


"""end of requirements"""


class User(Base):
    __tablename__ = 'users'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String, nullable=False)
    email: str = Column(String, nullable=False)
    # references the foreign key in UserInfo class table
    # change userlist=False to userlist=True to use one-to-many, False means one-to-one
    # backref allows to do info.user to get back to the user
    info: 'UserInfo' = relationship('UserInfo', uselist=False, backref="user")

    # for convenience
    @classmethod
    def create(cls, name, email):
        return cls(name=name, email=email)

    def __repr__(self):
        return f'<{self.__class__.__name__} name={self.name} email={self.email}>'


class UserInfo(Base):
    __tablename__ = 'userinfo'
    id: int = Column(Integer, primary_key=True)
    # allows other tables to reference this implicitly via relationships
    username: str = Column(String, ForeignKey('users.name'))
    group: str = Column(String, nullable=True)
    role: str = Column(String, nullable=True)

    # for convenience main
    @classmethod
    def create(cls, group, role, username):
        return cls(group=group, role=role, username=username)

    def __repr__(self):
        return f'<{self.__class__.__name__} group={self.group} role={self.role}>'


Base.metadata.create_all()

with transaction() as t:
    user = User.create('name', 'email')
    user.info_id = 1
    t.add(user)
    t.add(UserInfo.create('admins', 'admin', 'name'))

with transaction() as t:
    user: User = t.query(User).filter(User.name == 'name').one()
    print(user.info)
