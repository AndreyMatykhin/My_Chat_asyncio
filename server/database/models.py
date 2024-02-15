import uuid
from datetime import datetime as dt

from sqlalchemy import Column, String, LargeBinary, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

CBase = declarative_base()


class Client(CBase):
    """Table with clients"""
    __tablename__ = 'client'
    id = Column(String(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)
    username = Column(String(length=50), unique=True, nullable=False)
    password = Column(LargeBinary(), nullable=False)
    online_status = Column(Boolean(), default=False)


class History(CBase):
    """Table with history of client input"""
    __tablename__ = "history"
    id = Column(String(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)
    time = Column(DateTime(), default=dt.now(), nullable=False)
    ip_addr = Column(String(255))
    client_id = Column(String(length=36), ForeignKey('client.id'))
    client = relationship('Client', backref=backref('history', order_by=client_id))
