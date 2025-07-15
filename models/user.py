from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    username = Column(String)
    role = Column(String, default='student')

    # Исправлено: 'Group' вместо 'group'
    groups = relationship('Group', secondary='users_groups',  # Исправлено имя таблицы
                          back_populates='members')

    # Исправлено: 'Group' вместо 'group'
    own_groups = relationship('Group', back_populates='author', uselist=True)

    def is_admin(self) -> bool:
        return self.role == 'admin'

    def is_teacher(self) -> bool:
        return self.role == 'teacher'
