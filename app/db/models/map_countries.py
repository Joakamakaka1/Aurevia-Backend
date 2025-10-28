from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

class MapCountry(Base):
    __tablename__ = "map_countries"

    id = Column(Integer, primary_key=True, index=True)
    map_id = Column(Integer, ForeignKey("maps.id"), nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    
    # Campos adicionales útiles
    first_visited = Column(DateTime, default=datetime.now(timezone.utc))
    visit_count = Column(Integer, default=1)  # Cuántas veces ha visitado ese país
    last_visit = Column(DateTime, default=datetime.now(timezone.utc))

    # Relaciones
    map = relationship("Map", back_populates="map_countries")
    country = relationship("Country", back_populates="map_countries")