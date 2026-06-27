from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import (
    UUID as ID,
    uuid4 as id4
)

from src.database import Base
from src.database import CreatedAtUpdatedAtMixin


if TYPE_CHECKING:
    from src.modules.team_members import TeamMember
    from src.modules.user import User
    from src.modules.project import Project


class Team(Base, CreatedAtUpdatedAtMixin):
    __tablename__ = 'teams'

    # ======================
    # ==== MAIN COLUMNS ====
    # ======================
    id: Mapped[ID] = mapped_column(primary_key=True, default=id4)

    name: Mapped[str] = mapped_column(String, nullable=False)

    description: Mapped[str | None] = mapped_column(String, nullable=True, default=None)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


    # ======================
    # === RELATIONSHIPS ====
    # ======================
    creator_id: Mapped[ID | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'))

    created_by: Mapped['User'] = relationship(
        'User',
        back_populates='teams_established',
        foreign_keys=[creator_id]
    )


    projects: Mapped[list['Project']] = relationship(
        'Project',
        back_populates='team',
        foreign_keys='Project.team_id'
    )

    
    members: Mapped[list['TeamMember']] = relationship(
        'TeamMember',
        back_populates='team',
        cascade='all, delete-orphan'
    )


    def __repr__(self):
        return f"Team(id={self.id}, name={self.name}, is_active={self.is_active})"