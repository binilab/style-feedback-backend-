from datetime import datetime
from sqlalchemy import DateTime, String, func ,Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base 


class User(Base):
    __tablename__ = "users "

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] =mapped_column(String(255), unique=True, index=True,nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default='true')
    id_admin: Mapped[bool] = mapped_column(Boolean, nullable= False, default=False, server_default='false')
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False 
    )


