from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import Optional

class Country(Base):
    __tablename__ = "country"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    
    # Nuevos campos para datos de REST Countries API
    code_alpha2: Mapped[Optional[str]] = mapped_column(String(2), unique=True, nullable=True, index=True)
    code_alpha3: Mapped[Optional[str]] = mapped_column(String(3), unique=True, nullable=True, index=True)
    capital: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    subregion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    population: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    flag_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relaciones
    trips = relationship("Trip", back_populates="country")
    cities = relationship("City", back_populates="country")
