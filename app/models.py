from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()  # <-- this defines Base

class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(50), nullable=False)
    guessed_letters = Column(String(50), default="")
    attempts = Column(Integer, default=0)
    is_finished = Column(Boolean, default=False)
