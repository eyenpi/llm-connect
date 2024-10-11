import os
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import logging
from typing import Iterator

# Load environment variables
load_dotenv()

# Setup Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "55000")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Logs to a file
        logging.StreamHandler(),  # Also logs to the console
    ],
)
logger = logging.getLogger(__name__)


def create_database_if_not_exists() -> None:
    """Creates the database if it does not exist."""
    try:
        conn = psycopg2.connect(
            dbname="postgres",  # Connect to default 'postgres' database
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            logger.info(f"Database '{DB_NAME}' created.")
        else:
            logger.info(f"Database '{DB_NAME}' already exists.")

    except psycopg2.Error as e:
        logger.error(f"Database error: {e.pgcode} - {e.pgerror}")

    except Exception as e:
        logger.error(f"Unexpected error during database setup: {str(e)}")

    finally:
        cursor.close()
        conn.close()


# Ensuring the database is created if not exists
create_database_if_not_exists()

# Set up SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Iterator[Session]:
    """Creates a new database session/connection for a request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
