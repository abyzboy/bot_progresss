from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(String, default='Untitled')

    author_id = Column(Integer, ForeignKey('users.id'))

    author = relationship('User', back_populates='own_groups', lazy='selectin')

    members = relationship(
        'User',
        secondary='users_groups',
        back_populates='groups', lazy='selectin'
    )

    given_homeworks = relationship(
        'Homework', back_populates='group', uselist=True, lazy='selectin')
