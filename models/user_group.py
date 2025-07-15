from sqlalchemy import Column, Integer, ForeignKey
from database import Base


class UserGroup(Base):
    __tablename__ = 'users_groups'  # Исправлено имя таблицы

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'), primary_key=True)
