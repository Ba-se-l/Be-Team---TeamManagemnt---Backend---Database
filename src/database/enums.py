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

class TaskStatus(StrEnum):
    DONE = 'done'
    ACTIVE = 'active'
    IN_PROGRESS = 'in_progress'
    TODO = 'todo'
    IN_REVIEW = 'in_review'
    ARCHIVED = 'archived'

class TaskPriority(StrEnum):
    CRITICAL = 'critical'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'


class UserRoles(StrEnum):
    SUPER_ADMIN = 'super_admin'
    ADMIN = 'admin'
    DEVELOPER = 'developer'
    VIEWER = 'viewer'

class JobTitle(StrEnum):
    BACKEND_DEVELOPER = 'backend_developer'
    FRONTEND_DEVELOPER = 'frontend_developer'
    FLUTTER_DEVELOPER = 'flutter_developer'
    UIUX_DEVELOPER = 'UI_UX_developer'
    WEP_DEVELOPER = 'wep_developer'
    SOFTWERE_DEVELOPER = 'softwere_developer'
    