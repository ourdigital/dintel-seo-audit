import os
import sys
import nltk

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Set NLTK data path to ~/Utilities/nltk_data
nltk_data_path = os.path.expanduser("~/Utilities/nltk_data")
if os.path.exists(nltk_data_path):
    nltk.data.path.insert(0, nltk_data_path)
    print(f"Using NLTK data from: {nltk_data_path}")
else:
    print(f"NLTK data path not found: {nltk_data_path}")
    print("NLTK will use default data locations")

def init_db():
    """
    Initialize the database with all required tables.
    
    This function creates all database tables defined in the SQLAlchemy models
    and sets up the initial database structure for the SEO audit application.
    """
    from src.main import app, db
    
    with app.app_context():
        # Create all database tables
        db.create_all()
        print("Database has been initialized successfully.")
        print(f"Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Check if tables were created
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Created tables: {', '.join(tables)}")

if __name__ == "__main__":
    init_db()
