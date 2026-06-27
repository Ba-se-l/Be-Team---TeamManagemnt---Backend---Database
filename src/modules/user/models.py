from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import (
    UUID as ID,
    uuid4 as id4
)

from src.database import Base
from src.database import CreatedAtUpdatedAtMixin
from src.database import UserStatus, JobTitle

if TYPE_CHECKING:
    from src.modules.team import Team
    from src.modules.team_members import TeamMember
    from src.modules.project import Project
    from src.modules.task import Task


class User(Base, CreatedAtUpdatedAtMixin):
    __tablename__ = 'users'

    # ======================
    # ==== MAIN COLUMNS ====
    # ======================
    id: Mapped[ID] = mapped_column(primary_key=True, default=id4)

    name: Mapped[str] = mapped_column(String, nullable=False)
    
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    is_super_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), default=UserStatus.ONLINE)

    job_title: Mapped[JobTitle | None] = mapped_column(Enum(JobTitle), nullable=True, default=None)

    bio: Mapped[str | None] = mapped_column(String, nullable=True, default=None)



    # ======================
    # === RELATIONSHIPS ====
    # ======================
    
    projects_established: Mapped[list['Project']] = relationship(
        'Project',
        back_populates='created_by',
        foreign_keys='Project.creator_id'
    )
    

    teams_established: Mapped[list['Team']] = relationship(
        'Team',
        back_populates='created_by',
        foreign_keys='Team.creator_id'
    )

    teams_memberships: Mapped[list['TeamMember']] = relationship(
        'TeamMember',
        back_populates='member',
        foreign_keys='TeamMember.member_id',
        cascade='all, delete-orphan'
    )


    
    tasks_established: Mapped[list['Task']] = relationship(
        'Task',
        back_populates='created_by',
        foreign_keys='Task.creator_id'
    )

    tasks_assigned: Mapped[list['Task']] = relationship(
        'Task',
        back_populates='assignee_to',
        foreign_keys='Task.assignee_to_id'
    )


    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, email={self.email})"