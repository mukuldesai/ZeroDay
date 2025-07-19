from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database.setup import get_db
from auth.simple_auth import get_user_by_token
from auth.permissions import has_permission, Permission
from database.models import User
from typing import Optional

security = HTTPBearer(auto_error=False)

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    token = None
    
    if credentials:
        token = credentials.credentials
    else:
        token = request.cookies.get("session_token")
    
    if not token:
        return None
    
    user = get_user_by_token(token, db)
    return user

async def require_auth(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return current_user

async def require_demo_or_auth(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return current_user

def require_permission_middleware(permission: Permission):
    async def permission_check(
        current_user: User = Depends(require_auth)
    ) -> User:
        if not has_permission(current_user, permission):
            raise HTTPException(
                status_code=403, 
                detail=f"Insufficient permissions: {permission.value}"
            )
        return current_user
    return permission_check

async def optional_auth(
    current_user: Optional[User] = Depends(get_current_user)
) -> Optional[User]:
    return current_user