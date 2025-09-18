# app/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    games = relationship("Game", back_populates="user")


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, unique=True, index=True)
    difficulty = Column(String, nullable=True)

    games = relationship("Game", back_populates="word")


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    word_id = Column(Integer, ForeignKey("words.id"))
    status = Column(String, default="in_progress")  # in_progress, won, lost
    attempts_left = Column(Integer, default=6)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="games")
    word = relationship("Word", back_populates="games")
    guesses = relationship("Guess", back_populates="game", cascade="all, delete")


class Guess(Base):
    __tablename__ = "guesses"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    letter = Column(String(1))
    is_correct = Column(Boolean)
    guessed_at = Column(DateTime, default=datetime.utcnow)

    game = relationship("Game", back_populates="guesses")
