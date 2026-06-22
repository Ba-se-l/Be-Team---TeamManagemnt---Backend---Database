from sqlalchemy import String, Boolean, Enum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import (
    UUID as ID,
    uuid4 as id4
)

from src.database import Base
from src.database import CreatedAtUpdatedAtMixin

from src.modules.user import User
from src.modules.project import Project

class Team(Base, CreatedAtUpdatedAtMixin):
    __tablename__ = 'teams'

    # ======================
    # ==== MAIN COLUMNS ====
    # ======================
    id: Mapped[ID] = mapped_column(primary_key=True, default=id4)

    name: Mapped[str] = mapped_column(String, nullable=False)


    # ======================
    # === RELATIONSHIPS ====
    # ======================
    creator_id: Mapped[ID] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'))

    created_by: Mapped['User'] = relationship(
        back_populates='teams_established',
        foreign_keys=[creator_id]
    )


    project_id: Mapped[ID] = mapped_column(ForeignKey('project.id', ondelete='CASCADE'))
    
    project: Mapped['Project'] = relationship(
        back_populates='team',
        foreign_keys=[project_id],
        cascade='all, delete-orphan'
    )