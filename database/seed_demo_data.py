from sqlalchemy.orm import Session
from database.models import User, Organization
from database.setup import SessionLocal
from datetime import datetime
import json

def create_demo_users():
    db = SessionLocal()
    try:
        demo_users = [
            {
                "name": "Sarah Chen",
                "email": "sarah.chen@demo.com",
                "password_hash": "demo_hash_1",
                "is_demo": True
            },
            {
                "name": "Marcus Rodriguez", 
                "email": "marcus.rodriguez@demo.com",
                "password_hash": "demo_hash_2",
                "is_demo": True
            },
            {
                "name": "Alex Thompson",
                "email": "alex.thompson@demo.com", 
                "password_hash": "demo_hash_3",
                "is_demo": True
            }
        ]
        
        for user_data in demo_users:
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing_user:
                user = User(**user_data)
                db.add(user)
                db.flush()
                
                org = Organization(
                    name=f"{user_data['name'].split()[0]}'s Organization",
                    user_id=user.id
                )
                db.add(org)
        
        db.commit()
        
    finally:
        db.close()

def create_demo_organizations():
    db = SessionLocal()
    try:
        demo_orgs = [
            "TechStartup Inc",
            "DevCorp Solutions", 
            "Innovation Labs",
            "CodeCraft Studios",
            "NextGen Software"
        ]
        
        users = db.query(User).filter(User.is_demo == True).all()
        
        for i, org_name in enumerate(demo_orgs):
            if i < len(users):
                existing_org = db.query(Organization).filter(
                    Organization.name == org_name,
                    Organization.user_id == users[i].id
                ).first()
                
                if not existing_org:
                    org = Organization(
                        name=org_name,
                        user_id=users[i].id
                    )
                    db.add(org)
        
        db.commit()
        
    finally:
        db.close()

def seed_all_demo_data():
    create_demo_users()
    create_demo_organizations()

if __name__ == "__main__":
    seed_all_demo_data()