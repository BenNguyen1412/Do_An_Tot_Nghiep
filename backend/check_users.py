from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User

def check_all_users():
    """Kiểm tra toàn bộ tài khoản trong hệ thống"""
    db: Session = SessionLocal()
    
    try:
        print("=" * 100)
        print("DANH SÁCH TÀI KHOẢN TRONG HỆ THỐNG")
        print("=" * 100)
        
        users = db.query(User).all()
        
        if not users:
            print("\n❌ Không có tài khoản nào trong hệ thống")
            return
        
        print(f"\n✅ Tìm thấy {len(users)} tài khoản\n")
        
        for idx, user in enumerate(users, 1):
            print(f"\n{'='*100}")
            print(f"TÀI KHOẢN #{idx}")
            print(f"{'='*100}")
            print(f"📧 Email:           {user.email}")
            print(f"👤 Họ tên:          {user.full_name}")
            print(f"📞 Số điện thoại:   {user.phone_number or 'Chưa cập nhật'}")
            print(f"🔑 Role:            {user.role.upper()}")
            print(f"✅ Trạng thái:      {'Đang hoạt động' if user.is_active else 'Bị khóa'}")
            print(f"🔐 Hash password:   {user.hashed_password[:50]}...")
            print(f"   Độ dài hash:     {len(user.hashed_password)} ký tự")
            print(f"   Định dạng:       {'✅ bcrypt' if user.hashed_password.startswith('$2b$') else '❌ Không hợp lệ'}")
            
            
        
        print(f"\n{'='*100}")
        print("THỐNG KÊ THEO ROLE")
        print(f"{'='*100}")
        
        from collections import Counter
        role_counts = Counter(user.role for user in users)
        
        for role, count in role_counts.items():
            print(f"📊 {role.upper()}: {count} tài khoản")
        
        print(f"\n{'='*100}\n")
        
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_all_users()