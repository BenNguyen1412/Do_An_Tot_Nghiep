"""
Script to delete all bookings from the database
"""
from app.core.database import SessionLocal
from app.models.court import Booking

def delete_all_bookings():
    """Xóa toàn bộ bookings"""
    db = SessionLocal()
    try:
        # Get count before deletion
        total_bookings = db.query(Booking).count()
        
        if total_bookings == 0:
            print("✓ Không có booking nào để xóa")
            return
        
        # Delete all bookings
        db.query(Booking).delete()
        db.commit()
        
        print(f"✅ Đã xóa thành công {total_bookings} booking!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi khi xóa dữ liệu: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🗑️  Đang xóa toàn bộ bookings...\n")
    
    # Confirm before deletion
    confirm = input("⚠️  Bạn có chắc chắn muốn xóa TOÀN BỘ bookings? (yes/no): ")
    
    if confirm.lower() in ['yes', 'y']:
        delete_all_bookings()
    else:
        print("❌ Đã hủy thao tác xóa")
