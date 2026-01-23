"""
Script to add customer_name column to bookings table
Run this script to update the database schema
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from app.core.database import engine

def add_customer_name_column():
    """Add customer_name column to bookings table"""
    
    try:
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='bookings' AND column_name='customer_name';
            """))
            
            if result.fetchone():
                print("✅ Column 'customer_name' already exists in 'bookings' table")
                return
            
            # Add the column
            conn.execute(text("""
                ALTER TABLE bookings 
                ADD COLUMN customer_name VARCHAR;
            """))
            conn.commit()
            
            print("✅ Successfully added 'customer_name' column to 'bookings' table")
            
    except Exception as e:
        print(f"❌ Error adding column: {e}")
        raise

if __name__ == "__main__":
    print("Adding customer_name column to bookings table...")
    add_customer_name_column()
    print("Done!")
