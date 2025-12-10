from sqlalchemy import ForeignKey, String, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import Optional

class City(Base):
    __tablename__ = "city"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    latitude: Mapped[Optional[float]] = mapped_column(nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(nullable=True)
    
    # Nuevos campos para datos de GeoNames API
    population: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    geoname_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True, nullable=True, index=True)

    country_id: Mapped[int] = mapped_column(ForeignKey("country.id"), nullable=True)

    # Relaciones
    country = relationship("Country", back_populates="cities")
    
    # Índice compuesto para evitar ciudades duplicadas por país
    __table_args__ = (
        Index('idx_city_name_country', 'name', 'country_id', unique=True),
    )
