"""
Test script to directly call the notification API
"""
from app.crud.notification import get_user_notifications, get_unread_count
from app.core.database import SessionLocal

# Create database session
db = SessionLocal()

try:
    print("\n" + "="*50)
    print("Testing Notification API for User 22 (Owner)")
    print("="*50 + "\n")
    
    # Get notifications for user 22 (the owner)
    notifications = get_user_notifications(db, user_id=22, skip=0, limit=10)
    unread_count = get_unread_count(db, user_id=22)
    
    print(f"✅ Found {len(notifications)} notifications for user 22")
    print(f"✅ Unread count: {unread_count}\n")
    
    if notifications:
        for notif in notifications:
            print(f"ID: {notif.id}")
            print(f"Title: {notif.title}")
            print(f"Message: {notif.message}")
            print(f"Type: {notif.type}")
            print(f"Read: {notif.is_read}")
            print(f"Created: {notif.created_at}")
            print("-" * 50)
    else:
        print("❌ No notifications found!")
        
    # Also check for admins
    print("\n" + "="*50)
    print("Testing Notification API for User 18 (Admin)")
    print("="*50 + "\n")
    
    admin_notifications = get_user_notifications(db, user_id=18, skip=0, limit=10)
    admin_unread_count = get_unread_count(db, user_id=18)
    
    print(f"✅ Found {len(admin_notifications)} notifications for user 18")
    print(f"✅ Unread count: {admin_unread_count}\n")
    
finally:
    db.close()
