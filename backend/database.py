from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  # Set to True for SQL debugging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()

# Metadata for table operations
metadata = MetaData()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database initialization
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables initialized")

# Database connection test
def test_db_connection():
    """Test database connection"""
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False