from enum import Enum
from database.models import User

class UserRole(Enum):
    DEMO = "demo"
    USER = "user"
    ADMIN = "admin"

class Permission(Enum):
    READ_CHAT = "read_chat"
    WRITE_CHAT = "write_chat"
    UPLOAD_FILES = "upload_files"
    MANAGE_TASKS = "manage_tasks"
    ACCESS_ANALYTICS = "access_analytics"
    ADMIN_PANEL = "admin_panel"

ROLE_PERMISSIONS = {
    UserRole.DEMO: [
        Permission.READ_CHAT,
        Permission.WRITE_CHAT,
        Permission.ACCESS_ANALYTICS
    ],
    UserRole.USER: [
        Permission.READ_CHAT,
        Permission.WRITE_CHAT,
        Permission.UPLOAD_FILES,
        Permission.MANAGE_TASKS,
        Permission.ACCESS_ANALYTICS
    ],
    UserRole.ADMIN: [
        Permission.READ_CHAT,
        Permission.WRITE_CHAT,
        Permission.UPLOAD_FILES,
        Permission.MANAGE_TASKS,
        Permission.ACCESS_ANALYTICS,
        Permission.ADMIN_PANEL
    ]
}

def get_user_role(user: User) -> UserRole:
    if user.is_demo:
        return UserRole.DEMO
    if user.email.endswith("@admin.zeroday.dev"):
        return UserRole.ADMIN
    return UserRole.USER

def has_permission(user: User, permission: Permission) -> bool:
    user_role = get_user_role(user)
    return permission in ROLE_PERMISSIONS.get(user_role, [])

def require_permission(permission: Permission):
    def decorator(func):
        def wrapper(*args, **kwargs):
            user = kwargs.get('current_user')
            if not user or not has_permission(user, permission):
                raise PermissionError(f"User lacks required permission: {permission.value}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def get_user_permissions(user: User) -> list[Permission]:
    user_role = get_user_role(user)
    return ROLE_PERMISSIONS.get(user_role, [])