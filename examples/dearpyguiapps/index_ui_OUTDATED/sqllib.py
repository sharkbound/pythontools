from typing import Tuple, List

from sqlalchemy import create_engine, orm, Integer, String, Column, BLOB, exists
from sqlalchemy.ext.declarative import declarative_base
from pickle import dumps, loads

FILE = 'index.db'
engine = create_engine(f'sqlite:///{FILE}')
Base = declarative_base(bind=engine)
session_maker = orm.sessionmaker(bind=engine)
# noinspection PyTypeChecker
session: orm.Session = orm.scoped_session(session_maker)

DEFAULT_CONTENT = 'MISSING'


class Record(Base):
    __tablename__ = 'records'
    id = Column(Integer, primary_key=True, autoincrement=True)
    summary = Column(String, nullable=False, unique=True)
    location = Column(String, nullable=False, default='NONE')

    def add_tag(self, tag_name):
        if Tag.exists(tag_name.lower(), self.id):
            return
        Tag.new(tag_name.lower(), self.id)

    @staticmethod
    def exists_by_summary_exact(summary):
        return bool(session.query(Record).filter(Record.summary == summary.lower()).limit(1).count())

    @staticmethod
    def exists_by_id(id):
        return bool(session.query(Record).filter(Record.id == id).limit(1).count())

    @staticmethod
    def new(summary, location='', commit=True, stage=True):
        if Record.exists_by_summary_exact(summary.lower()):
            return session.query(Record).filter(Record.summary == summary.lower()).first()

        record = Record(summary=summary.lower(), location=location.lower())
        if stage:
            session.add(record)
        if commit:
            session.commit()
        return record


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    record_id = Column(Integer, nullable=False)

    @staticmethod
    def exists(tag_name, record_id) -> bool:
        return bool(session.query(Tag).filter(Tag.name == tag_name, Tag.record_id == record_id).limit(1).count())

    @staticmethod
    def new(name, record_id, commit=True, stage=True):
        if not AllTags.exists(name.lower()):
            AllTags.new(name.lower())

        if Tag.exists(name.lower(), record_id):
            return session.query(Tag).filter(Tag.name == name.lower()).first()

        tag = Tag(name=name.lower(), record_id=record_id)
        if stage:
            session.add(tag)
        if commit:
            session.commit()
        return tag

    def __repr__(self) -> str:
        return f'<Tag name={self.name} record_id={self.record_id}>'


class AllTags(Base):
    __tablename__ = 'all_tags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    @staticmethod
    def exists(tag_name) -> bool:
        return bool(session.query(AllTags).filter(AllTags.name == tag_name).limit(1).count())

    @staticmethod
    def new(name, commit=True, stage=True):
        if AllTags.exists(name.lower()):
            return session.query(AllTags).filter(AllTags.name == name.lower()).first()

        tag = AllTags(name=name.lower())
        if stage:
            session.add(tag)
        if commit:
            session.commit()
        return tag

    def __repr__(self) -> str:
        return f'<AllTags name={self.name}>'


Base.metadata.create_all(engine)


def query(*entities) -> orm.Query:
    return session.query(*entities)


def all_tags() -> List[AllTags]:
    return query(AllTags).all()


def commit():
    session.commit()


def load_tags_from_id_database(record_id):
    tags = query(Tag).filter(Tag.record_id == record_id).all()
    if tags:
        return [tag.name for tag in tags]
    return []
