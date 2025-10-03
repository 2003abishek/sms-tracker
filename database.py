from sqlalchemy import create_engine, Column, String, Text, DateTime, Float, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timezone, timedelta
import uuid
import os
import streamlit as st

Base = declarative_base()

class TrackingSession(Base):
    __tablename__ = 'tracking_sessions'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_phone = Column(String(20), nullable=False)
    recipient_phone = Column(String(20), nullable=False)
    message = Column(Text, nullable=True)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime)
    
    locations = relationship("LocationUpdate", back_populates="session", cascade="all, delete-orphan")

class LocationUpdate(Base):
    __tablename__ = 'location_updates'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(36), ForeignKey('tracking_sessions.id'), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    address = Column(Text, nullable=True)
    
    session = relationship("TrackingSession", back_populates="locations")

class Database:
    def __init__(self):
        # Use a writable database path for Streamlit Cloud
        try:
            # For Streamlit Cloud, use a path in the /tmp directory which is writable
            self.database_url = "sqlite:////tmp/safetrack.db"
        except:
            # Fallback for local development
            self.database_url = "sqlite:///safetrack.db"
            
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def init_db(self):
        try:
            Base.metadata.create_all(bind=self.engine)
        except Exception as e:
            st.error(f"Database initialization error: {e}")
            # Try with a different database path as fallback
            try:
                self.database_url = "sqlite:///safetrack.db"
                self.engine = create_engine(self.database_url)
                self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
                Base.metadata.create_all(bind=self.engine)
            except Exception as e2:
                st.error(f"Fallback database also failed: {e2}")
    
    def get_session(self):
        return self.SessionLocal()

# Initialize database
db = Database()
db.init_db()
