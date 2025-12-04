from sqlalchemy import String, Enum, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Campo role con valores predefinidos: user, admin, superadmin
    role: Mapped[str] = mapped_column(
        Enum("user", "admin", "superadmin", name="user_role_enum"), 
        nullable=False, 
        default="user",
        server_default="user"
    )

    trips = relationship("Trip", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")