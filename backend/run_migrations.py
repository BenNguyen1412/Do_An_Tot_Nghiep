"""
Migration runner script
Chạy các file SQL migration theo thứ tự
"""
import psycopg2
from pathlib import Path
from app.core.config import settings

def run_migration_file(cursor, filepath: Path):
    """Chạy một file SQL migration"""
    print(f"🔄 Đang chạy migration: {filepath.name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    try:
        cursor.execute(sql)
        print(f"✅ Hoàn thành: {filepath.name}")
        return True
    except Exception as e:
        print(f"❌ Lỗi khi chạy {filepath.name}: {e}")
        return False

def main():
    """Chạy tất cả migrations"""
    # Kết nối database
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_DATABASE,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Danh sách migrations theo thứ tự
    migration_files = [
        "migration_add_bank_account.sql",
        "migration_vietqr_payment.sql",
        "fix_booking_status.sql",
        "add_status_constraint.sql"
    ]
    
    print("=" * 60)
    print("🚀 BẮT ĐẦU CHẠY DATABASE MIGRATIONS")
    print("=" * 60)
    
    backend_path = Path(__file__).parent
    success_count = 0
    
    for migration_file in migration_files:
        filepath = backend_path / migration_file
        if filepath.exists():
            if run_migration_file(cursor, filepath):
                success_count += 1
            print()
        else:
            print(f"⚠️  Không tìm thấy file: {migration_file}")
            print()
    
    cursor.close()
    conn.close()
    
    print("=" * 60)
    print(f"✨ HOÀN THÀNH: {success_count}/{len(migration_files)} migrations thành công")
    print("=" * 60)

if __name__ == "__main__":
    main()
