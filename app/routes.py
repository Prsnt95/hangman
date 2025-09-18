from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db import SessionLocal, engine, Base
from app.models import User, Word, Game, Guess
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# Create all tables
Base.metadata.create_all(bind=engine)

# Request/Response models
class GuessRequest(BaseModel):
    letter: str
    game_id: int

class GameState(BaseModel):
    game_id: int
    word_length: int
    guessed_letters: List[str]
    correct_letters: List[str]
    incorrect_letters: List[str]
    word_progress: str  # e.g., "_ a _ _ l e"
    attempts_left: int
    max_attempts: int
    status: str  # active, won, lost, cancelled
    word_revealed: Optional[str] = None  # only shown when game is over

# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_word_progress(word_text: str, correct_letters: List[str]) -> str:
    """Generate word progress string like '_ a _ _ l e'"""
    return ' '.join([letter if letter.lower() in correct_letters else '_' for letter in word_text.lower()])

def get_game_state(game: Game, db: Session) -> GameState:
    """Get current game state with all progress info"""
    # Get the word
    word = db.query(Word).filter(Word.id == game.word_id).first()
    if not word:
        raise HTTPException(status_code=500, detail="Word not found for game")
    
    # Get all guesses for this game
    guesses = db.query(Guess).filter(Guess.game_id == game.id).all()
    
    guessed_letters = [guess.letter.lower() for guess in guesses]
    correct_letters = [guess.letter.lower() for guess in guesses if guess.is_correct]
    incorrect_letters = [guess.letter.lower() for guess in guesses if not guess.is_correct]
    
    # Check win condition - all letters in word have been guessed
    word_letters = set(word.text.lower())
    is_won = word_letters.issubset(set(correct_letters))
    
    # Game settings
    max_attempts = 6
    attempts_used = len(incorrect_letters)
    attempts_left = max_attempts - attempts_used
    is_lost = attempts_left <= 0
    
    # Update game status if needed
    if is_won and game.status == "active":
        game.status = "won"
        db.commit()
    elif is_lost and game.status == "active":
        game.status = "lost"
        db.commit()
    
    return GameState(
        game_id=game.id,
        word_length=len(word.text),
        guessed_letters=guessed_letters,
        correct_letters=correct_letters,
        incorrect_letters=incorrect_letters,
        word_progress=get_word_progress(word.text, correct_letters),
        attempts_left=attempts_left,
        max_attempts=max_attempts,
        status=game.status,
        word_revealed=word.text if game.status in ["won", "lost"] else None
    )

# Initialize test data
@router.post("/init-game-data")
def init_game_data(db: Session = Depends(get_db)):
    """Initialize game with sample words"""
    
    # Check if we already have data
    word_count = db.query(func.count(Word.id)).scalar()
    if word_count > 0:
        return {"message": "Game data already exists", "word_count": word_count}
    
    # Create test user
    test_user = User(username="player1")
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    # Add sample words for hangman
    sample_words = [
        "python", "javascript", "computer", "programming", "hangman",
        "challenge", "victory", "awesome", "fantastic", "wonderful",
        "amazing", "brilliant", "excellent", "spectacular", "incredible"
    ]
    
    for word_text in sample_words:
        word = Word(text=word_text)
        db.add(word)
    
    db.commit()
    
    return {
        "message": "Game data initialized",
        "user_id": test_user.id,
        "words_added": len(sample_words)
    }

# Start new game
@router.post("/new-game")
def new_game(db: Session = Depends(get_db)):
    """Start a new hangman game"""
    
    # Get or create user
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=400, detail="No users found. Run /init-game-data first.")
    
    # Cancel any active games for this user
    active_games = db.query(Game).filter(Game.user_id == user.id, Game.status == "active").all()
    for game in active_games:
        game.status = "cancelled"
    
    # Get random word
    word = db.query(Word).order_by(func.random()).first()
    if not word:
        raise HTTPException(status_code=400, detail="No words found. Run /init-game-data first.")
    
    # Create new game
    new_game = Game(user_id=user.id, word_id=word.id, status="active")
    db.add(new_game)
    db.commit()
    db.refresh(new_game)
    
    # Return initial game state
    game_state = get_game_state(new_game, db)
    
    return {
        "message": "New game started!",
        "game": game_state
    }

# Make a guess
@router.post("/guess")
def make_guess(guess_request: GuessRequest, db: Session = Depends(get_db)):
    """Make a letter guess in the game"""
    
    # Validate input
    letter = guess_request.letter.lower().strip()
    if len(letter) != 1 or not letter.isalpha():
        raise HTTPException(status_code=400, detail="Guess must be a single letter")
    
    # Get game
    game = db.query(Game).filter(Game.id == guess_request.game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if game.status != "active":
        raise HTTPException(status_code=400, detail=f"Game is {game.status}. Start a new game.")
    
    # Check if letter already guessed
    existing_guess = db.query(Guess).filter(
        Guess.game_id == game.id, 
        Guess.letter == letter
    ).first()
    if existing_guess:
        raise HTTPException(status_code=400, detail=f"Letter '{letter}' already guessed")
    
    # Get word and check if letter is correct
    word = db.query(Word).filter(Word.id == game.word_id).first()
    if not word:
        raise HTTPException(status_code=500, detail="Word not found")
    
    is_correct = letter in word.text.lower()
    
    # Save the guess
    new_guess = Guess(
        game_id=game.id,
        letter=letter,
        is_correct=is_correct
    )
    db.add(new_guess)
    db.commit()
    
    # Get updated game state
    game_state = get_game_state(game, db)
    
    result_message = "Correct guess! 🎉" if is_correct else "Incorrect guess! 😞"
    
    if game_state.status == "won":
        result_message = f"🎉 Congratulations! You won! The word was '{word.text}'"
    elif game_state.status == "lost":
        result_message = f"💀 Game over! The word was '{word.text}'"
    
    return {
        "message": result_message,
        "guess": {
            "letter": letter,
            "is_correct": is_correct
        },
        "game": game_state
    }

# Get current game state
@router.get("/game-state")
def get_current_game_state(db: Session = Depends(get_db)):
    """Get the current active game state"""
    
    # Get user's active game
    game = db.query(Game).filter(Game.status == "active").first()
    if not game:
        raise HTTPException(status_code=404, detail="No active game found. Start a new game!")
    
    game_state = get_game_state(game, db)
    
    return {
        "game": game_state
    }

# Get game by ID
@router.get("/game/{game_id}")
def get_game_by_id(game_id: int, db: Session = Depends(get_db)):
    """Get specific game state by ID"""
    
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game_state = get_game_state(game, db)
    
    return {
        "game": game_state
    }

# Get game statistics
@router.get("/stats")
def get_game_stats(db: Session = Depends(get_db)):
    """Get player statistics"""
    
    total_games = db.query(func.count(Game.id)).scalar()
    won_games = db.query(func.count(Game.id)).filter(Game.status == "won").scalar()
    lost_games = db.query(func.count(Game.id)).filter(Game.status == "lost").scalar()
    active_games = db.query(func.count(Game.id)).filter(Game.status == "active").scalar()
    
    win_rate = (won_games / total_games * 100) if total_games > 0 else 0
    
    return {
        "stats": {
            "total_games": total_games,
            "won_games": won_games,
            "lost_games": lost_games,
            "active_games": active_games,
            "win_rate": round(win_rate, 1)
        }
    }

# Simple test route
@router.get("/")
def root():
    return {"message": "Hangman Game API", "status": "ready"}