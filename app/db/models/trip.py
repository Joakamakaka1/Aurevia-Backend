from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from sqlalchemy.orm import relationship

class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = Column(String(255), nullable=False)
    description: Mapped[str] = Column(String(255), nullable=False)
    start_date: Mapped[str] = Column(String(255), nullable=False)
    end_date: Mapped[str] = Column(String(255), nullable=False)

    # user_id: Mapped[int] = Column(Integer, nullable=False)
    # user: Mapped["User"] = relationship("User", back_populates="trips")