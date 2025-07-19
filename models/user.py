from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    username = Column(String)
    role = Column(String, default='student')

    groups = relationship('Group', secondary='users_groups',
                          back_populates='members', lazy='selectin')

    own_groups = relationship(
        'Group', back_populates='author', uselist=True, lazy='selectin')

    def is_admin(self) -> bool:
        return self.role == 'admin'

    def is_teacher(self) -> bool:
        return self.role == 'teacher'
