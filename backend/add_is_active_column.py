from sqlalchemy import text
from app.core.database import engine

print("Adding is_active column to users table...")

with engine.connect() as conn:
    # Check if column exists
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='users' AND column_name='is_active'
    """))
    
    if result.fetchone() is None:
        # Add the column
        conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
        conn.commit()
        print("✅ Column is_active added successfully!")
    else:
        print("ℹ️ Column is_active already exists")

print("Done!")
