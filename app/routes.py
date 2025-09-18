

    
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Game, Base
from app.db import SessionLocal, engine

router = APIRouter()

# Ensure tables exist
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test route
@router.get("/")
def root():
    return{"hello" : "world"}



# Optional: Create a game to test insert
@router.get("/start")
def start_game(word: str | None = None, db: Session = Depends(get_db)):
    # If no word provided, pick a random existing word from games table
    if not word:
        # Try to select a random word from existing games
        random_game = db.query(Game).order_by(func.random()).first()
        if random_game and random_game.word:
            word = random_game.word
        else:
            # Fallback default if DB has no words
            word = "test"

    new_game = Game(word=word)
    db.add(new_game)
    db.commit()
    db.refresh(new_game)
    return {"id": new_game.id, "word": new_game.word}
