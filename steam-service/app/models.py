from app.database import Base
from sqlalchemy.orm import Mapped,mapped_column
from uuid import UUID
from sqlalchemy import UUID as SUUID
class User_steam(Base):
    __tablename__="user_steam"
    user_id: Mapped[UUID] = mapped_column(SUUID(as_uuid=True), primary_key=True)
    steam_id:Mapped[str]=mapped_column(unique=True)