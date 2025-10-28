from sqlalchemy import Column, Integer, String
from app.db.base import Base
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from datetime import datetime, timezone
from sqlalchemy.orm import relationship

class Map(Base):
    __tablename__ = "maps"

    id = Column(Integer, primary_key=True)
    countries_visited = Column(Integer, default=0)
    percent_world_visited = Column(Float, default=0.0)
    map_image_url = Column(String(255), nullable=True)
    last_updated = Column(DateTime, default=datetime.now(timezone.utc))

    # Relationship to User
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    user = relationship("User", back_populates="map")
        
    # Relationship to MapCountry
    map_countries = relationship("MapCountry", back_populates="map", cascade="all, delete-orphan")



    