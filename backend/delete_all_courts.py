"""
Script to delete all courts from the database
"""
from app.core.database import SessionLocal
from app.models.court import Court, IndividualCourt, Booking

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
        print("\n✅ Đã xóa toàn bộ dữ liệu sân thành công!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Lỗi khi xóa dữ liệu: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🗑️  Đang xóa toàn bộ dữ liệu sân...\n")
    delete_all_courts()
