# app/routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db import SessionLocal, engine, Base
from app.models import User, Word, Game, Guess
from fastapi import HTTPException

router = APIRouter()

# Create all tables
Base.metadata.create_all(bind=engine)

# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Simple test route
@router.get("/")
def root():
    return {"hello": "world"}

# Test DB route
@router.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    game_count = db.query(func.count(Game.id)).scalar()

    if game_count == 0:
        # Create test user
        test_user = User(username="testuser")
        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        # Create test word
        test_word = Word(text="example")
        db.add(test_word)
        db.commit()
        db.refresh(test_word)

        # Create test game
        test_game = Game(user_id=test_user.id, word_id=test_word.id)
        db.add(test_game)
        db.commit()
        db.refresh(test_game)

        return {
            "message": "Test data created",
            "user": {"id": test_user.id, "username": test_user.username},
            "word": {"id": test_word.id, "text": test_word.text},
            "game": {"id": test_game.id, "status": test_game.status},
        }

    return {"message": f"Database already has {game_count} game(s)"}

@router.get("/get-word/{word_id}")
def get_word(word_id: int, db: Session = Depends(get_db)):
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    return {"id": word.id, "text": word.text, "difficulty": word.difficulty}
