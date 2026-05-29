from app.database import Base
from uuid import UUID, uuid4
from sqlalchemy import UUID as SUUID
from sqlalchemy.orm import Mapped,mapped_column
class User(Base):
    __tablename__="users"
    id: Mapped[UUID] = mapped_column(SUUID(as_uuid=True), primary_key=True, default=uuid4)
    username:Mapped[str]=mapped_column(unique=True)
    email:Mapped[str]=mapped_column(unique=True)
    password:Mapped[str]=mapped_column()