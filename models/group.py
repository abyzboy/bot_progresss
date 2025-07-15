from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(String, default='Untitled')

    # Добавлен ForeignKey
    author_id = Column(Integer, ForeignKey('users.id'))

    # Исправлено: 'User' вместо 'user'
    author = relationship('User', back_populates='own_groups')

    # Исправлено: 'User' вместо 'user'
    members = relationship(
        'User',
        secondary='users_groups',  # Исправлено имя таблицы
        back_populates='groups'
    )
