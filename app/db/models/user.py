from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = Column(String(255), unique=True, nullable=False)
    username: Mapped[str] = Column(String(255), unique=True, nullable=False)
    password: Mapped[str] = Column(String(255), nullable=False)

    ## trips: Mapped[list["Trip"]] = relationship("Trip", back_populates="user")