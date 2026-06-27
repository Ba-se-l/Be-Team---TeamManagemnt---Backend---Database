from sqlalchemy import Column, ForeignKey, Table

from src.database import Base

ProjectsTechnologies = Table(
    'projects_technologies',
    Base.metadata,
    Column('project_id', ForeignKey('projects.id', ondelete='CASCADE'), primary_key=True),
    Column('technology_id', ForeignKey('technologies.id', ondelete='CASCADE'), primary_key=True)
)