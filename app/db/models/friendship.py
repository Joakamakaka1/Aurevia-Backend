# from sqlalchemy import String
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from app.db.base import Base
# from sqlalchemy import ForeignKey

# class Friendship(Base):
#     __tablename__ = "friendships"

#     id: Mapped[int] = mapped_column(primary_key=True)
    
#     #Relacion con la tabla user para encontrar el usuario
#     user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
#     #Relacion con la tabla user para encontrar el amigo
#     friend_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
#     status: Mapped[str] = mapped_column(String(20), default="pending")

#     user = relationship("User", foreign_keys=[user_id], back_populates="friendships")
#     friend = relationship("User", foreign_keys=[friend_id])
