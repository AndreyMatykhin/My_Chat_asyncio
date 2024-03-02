import uuid
from datetime import datetime as dt

from sqlalchemy import Column, String, LargeBinary, Boolean, DateTime, ForeignKey, UniqueConstraint, Unicode
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


class Contacts(CBase):
    """Table with contacts(friends) of client"""
    __tablename__ = 'contacts'
    __table_args__ = (UniqueConstraint('client_id', 'contact_id', name='unique_contact'),)
    id = Column(String(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)
    client_id = Column(String(length=36), ForeignKey('client.id'))
    contact_id = Column(String(length=36), ForeignKey('client.id'))
    client = relationship('Client', foreign_keys=[client_id])
    contact = relationship('Client', foreign_keys=[contact_id])


class Messages(CBase):
    """Table with messages of client"""
    __tablename__ = 'messages'
    id = Column(String(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)
    client_id = Column(String(length=36), ForeignKey('client.id'))
    contact_id = Column(String(length=36), ForeignKey('client.id'))
    time = Column(DateTime(), default=dt.now(), nullable=False)
    client = relationship('Client', foreign_keys=[client_id])
    contact = relationship('Client', foreign_keys=[contact_id])
    message = Column(Unicode())