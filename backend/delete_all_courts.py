"""
Script to delete all courts from the database and their images
"""
from pathlib import Path
from app.core.database import SessionLocal
from app.models.court import Court, IndividualCourt, Booking

def delete_court_images():
    """Xóa tất cả hình ảnh trong thư mục uploads/courts"""
    courts_dir = Path("uploads/courts")
    
    if not courts_dir.exists():
        print("⚠️  Thư mục uploads/courts không tồn tại")
        return 0
    
    try:
        # Lấy danh sách file (giữ lại .gitkeep)
        files = [f for f in courts_dir.iterdir() if f.is_file() and f.name != '.gitkeep']
        total_files = len(files)
        
        if total_files == 0:
            print("✓ Không có hình ảnh nào để xóa")
            return 0
        
        # Xóa từng file
        deleted_count = 0
        for file in files:
            try:
                file.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"   ⚠️  Không thể xóa {file.name}: {e}")
        
        print(f"✓ Đã xóa {deleted_count} hình ảnh")
        return deleted_count
        
    except Exception as e:
        print(f"❌ Lỗi khi xóa hình ảnh: {e}")
        return 0

def delete_all_courts():
    db = SessionLocal()
    try:
        # Delete all bookings first (foreign key constraint)
        bookings_count = db.query(Booking).count()
        db.query(Booking).delete()
        print(f"✓ Đã xóa {bookings_count} bookings")
        
        # Delete all individual courts
        individual_courts_count = db.query(IndividualCourt).count()
        db.query(IndividualCourt).delete()
        print(f"✓ Đã xóa {individual_courts_count} sân con")
        
        # Delete all courts
        courts_count = db.query(Court).count()
        db.query(Court).delete()
        print(f"✓ Đã xóa {courts_count} sân chính")
        
        db.commit()
        
        # Delete court images
        delete_court_images()
        
        print("\n✅ Đã xóa toàn bộ dữ liệu sân và hình ảnh thành công!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Lỗi khi xóa dữ liệu: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🗑️  Đang xóa toàn bộ dữ liệu sân...\n")
    delete_all_courts()
