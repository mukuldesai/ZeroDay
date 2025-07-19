from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.models import User, UserSession
from database.setup import get_db
import secrets
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def create_session_token() -> str:
    return secrets.token_urlsafe(32)

def create_user_session(user_id: int, db: Session) -> str:
    token = create_session_token()
    expires_at = datetime.utcnow() + timedelta(days=30)
    
    session = UserSession(
        user_id=user_id,
        session_token=token,
        expires_at=expires_at
    )
    
    db.add(session)
    db.commit()
    return token

def authenticate_user(email: str, password: str, db: Session) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    
    if user.is_demo or verify_password(password, user.password_hash):
        return user
    
    return None

def get_user_by_token(token: str, db: Session) -> User:
    session = db.query(UserSession).filter(
        UserSession.session_token == token,
        UserSession.expires_at > datetime.utcnow()
    ).first()
    
    if session:
        return session.user
    return None

def logout_user(token: str, db: Session) -> bool:
    session = db.query(UserSession).filter(
        UserSession.session_token == token
    ).first()
    
    if session:
        db.delete(session)
        db.commit()
        return True
    return False

def cleanup_expired_sessions(db: Session):
    expired_sessions = db.query(UserSession).filter(
        UserSession.expires_at <= datetime.utcnow()
    ).all()
    
    for session in expired_sessions:
        db.delete(session)
    
    db.commit()