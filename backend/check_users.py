import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set UTF-8 encoding for output
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.core.config import settings

def main():
    # Create engine
    engine = create_engine(settings.DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(bind=engine)
    
    # Query users
    db = SessionLocal()
    
    try:
        users = db.query(User).all()
        
        print("\n" + "="*80)
        print(f"📊 TỔNG SỐ USERS: {len(users)}")
        print("="*80 + "\n")
        
        if not users:
            print("❌ Không có user nào trong database!")
            return
        
        for idx, user in enumerate(users, 1):
            print(f"👤 USER #{idx}")
            print(f"   ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Họ Tên: {user.full_name}")
            print(f"   Loại TK: {user.role.value}")
            print(f"   SĐT: {user.phone_number or 'Chưa có'}")
            print(f"   Địa chỉ: {user.address or 'Chưa có'}")
            print(f"   Ngày tạo: {user.created_at}")
            print("-" * 80)
        
        # Statistics by role
        print("\n📈 THỐNG KÊ THEO LOẠI TÀI KHOẢN:")
        from collections import Counter
        role_counts = Counter(user.role.value for user in users)
        for role, count in role_counts.items():
            print(f"   {role}: {count} người")
        
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()