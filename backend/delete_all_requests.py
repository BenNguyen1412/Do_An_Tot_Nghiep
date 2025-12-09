"""
Script to delete all court requests from the database
"""
from app.core.database import SessionLocal
from app.models import CourtRequest

def delete_all_requests():
    """Xóa toàn bộ court requests"""
    db = SessionLocal()
    try:
        # Get count before deletion
        total_requests = db.query(CourtRequest).count()
        
        if total_requests == 0:
            print("✓ Không có yêu cầu nào để xóa")
            return
        
        # Delete all court requests
        db.query(CourtRequest).delete()
        db.commit()
        
        print(f"✅ Đã xóa thành công {total_requests} yêu cầu tạo sân!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi khi xóa dữ liệu: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🗑️  Đang xóa toàn bộ yêu cầu tạo sân...\n")
    
    # Confirm before deletion
    confirm = input("⚠️  Bạn có chắc chắn muốn xóa TOÀN BỘ yêu cầu? (yes/no): ")
    
    if confirm.lower() in ['yes', 'y']:
        delete_all_requests()
    else:
        print("❌ Đã hủy thao tác xóa")
