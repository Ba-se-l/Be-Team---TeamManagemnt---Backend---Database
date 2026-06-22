from sqlalchemy import String, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import (
    UUID as ID,
    uuid4 as id4
)

from src.database import Base
from src.database import CreatedAtUpdatedAtMixin
from src.database import UserStatus

from src.modules.project import Project

class User(Base, CreatedAtUpdatedAtMixin):
    __tablename__ = 'users'

    # ======================
    # ==== MAIN COLUMNS ====
    # ======================
    id: Mapped[ID] = mapped_column(primary_key=True, default=id4)

    name: Mapped[str] = mapped_column(String, nullable=False)
    
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    is_active: Mapped[Boolean] = mapped_column(Boolean, default=True)

    is_super_admin: Mapped[Boolean] = mapped_column(Boolean, default=False)

    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), default=UserStatus.ONLINE)


    # ======================
    # === RELATIONSHIPS ====
    # ======================
    projects_established: Mapped[list['Project']] = relationship(
        back_populates='created_by',
        foreign_keys='Project.creator_id'
    )