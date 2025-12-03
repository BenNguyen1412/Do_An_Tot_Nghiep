"""
Script to create notification and court_request tables
Run this to add new tables to existing database
"""
from app.core.database import engine, Base
from app.models import Notification, CourtRequest

def create_tables():
    """Create notification and court_request tables"""
    print("Creating notification and court_request tables...")
    Base.metadata.create_all(bind=engine, tables=[
        Notification.__table__,
        CourtRequest.__table__
    ])
    print("✅ Tables created successfully!")

if __name__ == "__main__":
    create_tables()
