from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class StatusEnum(enum.Enum):
    safe = "safe"
    dangerous = "dangerous"
    unknown = "unknown"

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_hash = Column(String(255), unique=True, nullable=False)
    last_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    status = Column(Enum(StatusEnum), nullable=False)
    amount = Column(Integer, default=1)

class UserMessage(Base):
    __tablename__ = 'user_messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False)
    local_id = Column(String(255), nullable=False)
    message_id = Column(Integer, ForeignKey('messages.id'), nullable=False)
    
    message = relationship('Message', backref='user_messages')