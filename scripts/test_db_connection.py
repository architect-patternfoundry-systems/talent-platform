"""Test database connection"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.database import engine, Base
from src.core.config import settings


def test_connection():
    """Test database connection"""
    print(f"Testing database connection...")
    print(f"Database URL: {settings.database_url}")
    
    try:
        # Test connection
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            print(f"✓ Database connection successful")
            print(f"  Result: {result.fetchone()}")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
