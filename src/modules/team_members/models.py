from typing import TYPE_CHECKING
from sqlalchemy import Enum, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import (
    UUID as ID
)
from datetime import datetime

from src.database import Base, UserRoles

if TYPE_CHECKING:
    from src.modules.user import User
    from src.modules.team import Team

class TeamMember(Base):
    __tablename__ = 'team_members'

    # ======================
    # === RELATIONSHIPS ====
    # ======================
    member_id: Mapped[ID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)

    team_id: Mapped[ID] = mapped_column(ForeignKey('teams.id', ondelete='CASCADE'), primary_key=True)

    role: Mapped[UserRoles] = mapped_column(Enum(UserRoles), nullable=False)

    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


    def __repr__(self):
        return f"TeamMember(member_id={self.member_id}, team_id={self.team_id}, role={self.role})"
    
    member: Mapped['User'] = relationship(
        'User',
        back_populates='teams_memberships',
        foreign_keys=[member_id]
    )

    
    team: Mapped['Team'] = relationship(
        'Team',
        back_populates='members',
        foreign_keys=[team_id]
    )
    

