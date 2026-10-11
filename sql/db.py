from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv("sql/.env.sql")  # Load environment variables from .env file

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


CA_PATH = "C:/Users/geeth.madhu/global-bundle.pem"

# Build Database URL (using pymysql driver)
# Note: If your password contains special characters like '@', ':', or '/', 
# encode it using urllib.parse.quote_plus(DB_PASS)
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Configure SSL via connect_args
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "ssl": {
            "ca": CA_PATH,
            "check_hostname": True  # Enforces hostname verification (like VERIFY_IDENTITY)
        }
    },
    pool_recycle=3600,
    echo=False  # Set to True if you want to view raw SQL queries
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

print(f"Database URL configured for host={DB_HOST} port={DB_PORT} db={DB_NAME} (credentials hidden).")

