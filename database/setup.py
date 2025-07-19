from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./zeroday.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    create_tables()
    db = SessionLocal()
    try:
        from database.models import User
        demo_user = db.query(User).filter(User.email == "demo@zeroday.dev").first()
        if not demo_user:
            demo_user = User(
                name="Demo User",
                email="demo@zeroday.dev",
                password_hash="demo_hash",
                is_demo=True
            )
            db.add(demo_user)
            db.commit()
    finally:
        db.close()