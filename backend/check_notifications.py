"""
Script to check notifications in database
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings, get_database_url
from app.models.notification import Notification
from app.models.user import User

# Create engine
engine = create_engine(get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_notifications():
    db = SessionLocal()
    try:
        # Get all notifications
        notifications = db.query(Notification).all()
        print(f"\n📋 Total notifications: {len(notifications)}\n")
        
        for notif in notifications:
            user = db.query(User).filter(User.id == notif.user_id).first()
            print(f"ID: {notif.id}")
            print(f"User: {user.full_name if user else 'Unknown'} (ID: {notif.user_id})")
            print(f"Title: {notif.title}")
            print(f"Message: {notif.message}")
            print(f"Type: {notif.type}")
            print(f"Read: {notif.is_read}")
            print(f"Created: {notif.created_at}")
            print("-" * 50)
            
    finally:
        db.close()

if __name__ == "__main__":
    check_notifications()
