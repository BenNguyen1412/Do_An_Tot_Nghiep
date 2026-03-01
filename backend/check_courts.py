import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.court import Court

def check_courts():
    db = SessionLocal()
    try:
        # Get all courts
        courts = db.query(Court).all()
        
        print(f"\n{'='*60}")
        print(f"TỔNG SỐ SÂN TRONG HỆ THỐNG: {len(courts)}")
        print(f"{'='*60}\n")
        
        if courts:
            print("DANH SÁCH CÁC SÂN:\n")
            for i, court in enumerate(courts, 1):
                print(f"{i}. ID: {court.id}")
                print(f"   Tên: {court.name}")
                print(f"   Địa chỉ: {court.address}, {court.district}, {court.city}")
                print(f"   Số sân: {court.court_quantity}")
                print(f"   Chủ sân ID: {court.owner_id}")
                print(f"   Trạng thái: {'Hoạt động' if court.is_active else 'Không hoạt động'}")
                print(f"   Giờ mở cửa: {court.opening_time} - {court.closing_time}")
                print(f"   Số hình ảnh: {len(court.images) if court.images else 0}")
                if court.images:
                    for j, img in enumerate(court.images, 1):
                        print(f"      Ảnh {j}: {img}")
                print(f"   Ngày tạo: {court.created_at}")
                print("-" * 60)
        else:
            print("⚠️  Chưa có sân nào trong hệ thống!")
            print("\nGợi ý:")
            print("- Đăng nhập với tài khoản owner")
            print("- Tạo sân mới tại trang quản lý của chủ sân")
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_courts()
