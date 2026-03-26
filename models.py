from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class ShortenedURL(Base):
    __tablename__ = "shortened_urls"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(Text, nullable=False)
    short_code = Column(String(20), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    total_clicks = Column(Integer, default=0)

    clicks = relationship("ClickEvent", back_populates="url", cascade="all, delete-orphan")


class ClickEvent(Base):
    __tablename__ = "click_events"

    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, ForeignKey("shortened_urls.id"), nullable=False)

    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    country = Column(String(100), nullable=True)
    device_type = Column(String(50), nullable=True)
    browser = Column(String(100), nullable=True)

    clicked_at = Column(DateTime, default=datetime.utcnow)

    url = relationship("ShortenedURL", back_populates="clicks")