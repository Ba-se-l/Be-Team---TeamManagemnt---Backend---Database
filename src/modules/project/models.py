from typing import TYPE_CHECKING
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
from src.modules.m2m import ProjectsTechnologies

if TYPE_CHECKING:
    from src.modules.user import User
    from src.modules.team import Team
    from src.modules.task import Task
    from src.modules.technology import Technology


class Project(Base, CreatedAtUpdatedAtMixin):
    __tablename__ = 'projects'

    # ======================
    # ==== MAIN COLUMNS ====
    # ======================
    id: Mapped[ID] = mapped_column(primary_key=True, default=id4)

    title: Mapped[str] = mapped_column(String, nullable=False)

    short_description: Mapped[str] = mapped_column(String, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.TODO)

    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    

    def __repr__(self):
        return f"Project(id={self.id}, title={self.title}, status={self.status})"
    
    # ======================
    # === RELATIONSHIPS ====
    # ======================
    creator_id: Mapped[ID | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'))

    created_by: Mapped['User'] = relationship(
        'User',
        back_populates='projects_established',
        foreign_keys=[creator_id]
    )


    team_id: Mapped[ID | None] = mapped_column(ForeignKey('teams.id', ondelete='SET NULL'))
    
    team: Mapped['Team'] = relationship(
        'Team',
        back_populates='projects',
        foreign_keys=[team_id]
    )
    

    tasks: Mapped[list['Task']] = relationship(
        'Task',
        back_populates='project',
        foreign_keys='Task.project_id',
        cascade='all, delete-orphan'
    )

    technologies: Mapped[list['Technology']] = relationship(
        'Technology',
        back_populates='projects',
        secondary=ProjectsTechnologies
    )
