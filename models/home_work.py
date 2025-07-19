from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Homework(Base):
    __tablename__ = 'homeworks'
    id = Column(Integer, primary_key=True)
    theme = Column(String)
    format_message = Column(String(10))
    data = Column(String)
    teacher_id = Column(Integer)
    date = Column(String)
    group_id = Column(Integer, ForeignKey('groups.id'))
    group = relationship(
        'Group', back_populates='given_homeworks', lazy='selectin')
