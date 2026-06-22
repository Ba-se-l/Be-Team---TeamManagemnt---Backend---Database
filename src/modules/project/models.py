from sqlalchemy import String, Boolean, Enum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import (
    UUID as ID,
    uuid4 as id4
)

from src.database import Base
from src.database import CreatedAtUpdatedAtMixin
from src.database import ProjectStatus

from src.modules.user import User
from src.modules.team import Team



class Project(Base, CreatedAtUpdatedAtMixin):
    __tablename__ = 'projects'

    # ======================
    # ==== MAIN COLUMNS ====
    # ======================
    id: Mapped[ID] = mapped_column(primary_key=True, default=id4)

    title: Mapped[str] = mapped_column(String, nullable=False)

    short_description: Mapped[str] = mapped_column(String, nullable=False)

    is_active: Mapped[Boolean] = mapped_column(Boolean, nullable=False)

    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), nullable=False)

    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    
    # ======================
    # === RELATIONSHIPS ====
    # ======================
    creator_id: Mapped[ID] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'))

    created_by: Mapped['User'] = relationship(
        back_populates='projects_established',
        foreign_keys=[creator_id]
    )


    team_id: Mapped[ID] = mapped_column(ForeignKey('teams.id', ondelete='SET NULL'))
    
    team: Mapped['Team'] = relationship(
        back_populates='project',
        foreign_keys=[team_id]
    )