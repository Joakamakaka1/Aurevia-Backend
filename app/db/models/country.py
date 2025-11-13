from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Country(Base):
    __tablename__ = "country"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)