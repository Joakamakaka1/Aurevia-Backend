import datetime
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.db.base import Base

class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    iso_code = Column(String(3), unique=True, nullable=False)  # 'ES', 'FR'

    continent = Column(String(50), nullable=True)
    region = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    trips = relationship("Trip", back_populates="country", cascade="all, delete-orphan")
