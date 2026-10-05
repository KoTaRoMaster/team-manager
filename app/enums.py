from enum import Enum

class UserRole(str, Enum):
    MEMBER = "member"
    MANAGER = "manager"
    ADMIN = "admin"


class TeamRole(str, Enum):
    MEMBER = "member"
    MANAGER = "manager"
    DEVELOPER = "developer"
    TESTER = "tester"

class TaskStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"