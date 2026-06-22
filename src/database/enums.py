from enum import StrEnum


class UserStatus(StrEnum):
    ONLINE = 'online'
    OFFLINE = 'offline'

class ProjectStatus(StrEnum):
    DONE = 'done'
    ACTIVE = 'active'
    IN_PROGRESS = 'in_progress'
    TODO = 'todo'
    IN_REVIEW = 'in_review'
    ARCHIVED = 'archived'
