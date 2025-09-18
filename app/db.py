# app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+psycopg2://hangman_user:hangman_pass@db:5432/hangman_db"

# SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# SessionLocal class to create DB sessions
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base class for models
Base = declarative_base()
