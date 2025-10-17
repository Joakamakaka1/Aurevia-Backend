from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)

    trips = relationship("trips", back_populates="user", cascade="all, delete-orphan")

    trips = relationship("trips", back_populates="user", cascade="all, delete-orphan")

    map = relationship("Map", back_populates="user", uselist=False, cascade="all, delete-orphan")