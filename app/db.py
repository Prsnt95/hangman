from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Connection string format:
# postgresql+psycopg2://username:password@host:port/database

DATABASE_URL = "postgresql+psycopg2://hangman_user:hangman_pass@db:5432/hangman_db"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

Base = declarative_base()

