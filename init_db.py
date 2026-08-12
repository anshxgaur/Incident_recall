"""Initialize the database schema."""
import os
import sys
from dotenv import load_dotenv

load_dotenv(override=True)

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from new_ingest import connect_db, setup_postgres

def init_db():
    """Create the incidents table if it doesn't exist."""
    try:
        with connect_db() as conn:
            setup_postgres(conn)
            print("✓ Database schema initialized successfully!")
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_db()
