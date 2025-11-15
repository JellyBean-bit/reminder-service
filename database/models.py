from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from database.base import Base


class User(Base):
    """Модель пользователя бота."""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True)
    is_blocked = Column(Boolean, default=False)
    reason = Column(String)

    reminders = relationship("Reminder", back_populates="user")


class Reminder(Base):
    """Модель напоминания."""
    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    text = Column(String)
    remind_at = Column(DateTime)
    is_sent = Column(Boolean, default=False)

    user = relationship("User", back_populates="reminders")
