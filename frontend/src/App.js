import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './index.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [gameState, setGameState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [guessInput, setGuessInput] = useState('');
  const [message, setMessage] = useState('');
  const [stats, setStats] = useState(null);

  // API call function
  const makeApiCall = async (endpoint, method = 'GET', data = null) => {
    setLoading(true);
    try {
      const config = {
        method,
        url: `${API_BASE_URL}${endpoint}`,
        headers: {
          'Content-Type': 'application/json',
        },
      };

      if (data && method !== 'GET') {
        config.data = data;
      }

      const response = await axios(config);
      return response.data;
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message;
      setMessage(`Error: ${errorMsg}`);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Initialize game data
  const initGameData = async () => {
    try {
      const result = await makeApiCall('/init-game-data', 'POST');
      setMessage(result.message);
      loadStats();
    } catch (error) {
      console.error('Failed to init game data:', error);
    }
  };

  // Start new game
  const startNewGame = async () => {
    try {
      const result = await makeApiCall('/new-game', 'POST');
      setGameState(result.game);
      setMessage(result.message);
      setGuessInput('');
      loadStats();
    } catch (error) {
      console.error('Failed to start new game:', error);
    }
  };

  // Make a guess
  const makeGuess = async () => {
    if (!guessInput.trim() || !gameState) return;

    const letter = guessInput.toLowerCase().trim();
    if (letter.length !== 1 || !/[a-z]/.test(letter)) {
      setMessage('Please enter a single letter');
      return;
    }

    try {
      const result = await makeApiCall('/guess', 'POST', {
        letter: letter,
        game_id: gameState.game_id
      });
      
      setGameState(result.game);
      setMessage(result.message);
      setGuessInput('');
      loadStats();
    } catch (error) {
      console.error('Failed to make guess:', error);
    }
  };

  // Load current game state
  const loadCurrentGame = async () => {
    try {
      const result = await makeApiCall('/game-state', 'GET');
      setGameState(result.game);
      setMessage('Game loaded!');
    } catch (error) {
      setMessage('No active game found. Start a new game!');
      console.error('No active game:', error);
    }
  };

  // Load game statistics
  const loadStats = async () => {
    try {
      const result = await makeApiCall('/stats', 'GET');
      setStats(result.stats);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  // Handle enter key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !loading && gameState?.status === 'active') {
      makeGuess();
    }
  };

  // Load game and stats on component mount
  useEffect(() => {
    loadCurrentGame();
    loadStats();
  }, []);

  // Render hangman drawing
  const renderHangman = (attemptsLeft, maxAttempts) => {
    const parts = [
      '  +---+',
      '  |   |',
      `  ${attemptsLeft <= 5 ? 'O' : ' '}   |`,
      ` ${attemptsLeft <= 3 ? '/' : ' '}${attemptsLeft <= 4 ? '|' : ' '}${attemptsLeft <= 2 ? '\\' : ' '}  |`,
      ` ${attemptsLeft <= 1 ? '/' : ' '} ${attemptsLeft <= 0 ? '\\' : ' '}  |`,
      '      |',
      '========='
    ];
    return parts.join('\n');
  };

  // Render alphabet for visual feedback
  const renderAlphabet = () => {
    const alphabet = 'abcdefghijklmnopqrstuvwxyz'.split('');
    return (
      <div className="alphabet">
        {alphabet.map(letter => {
          const isGuessed = gameState?.guessed_letters.includes(letter);
          const isCorrect = gameState?.correct_letters.includes(letter);
          const isIncorrect = gameState?.incorrect_letters.includes(letter);
          
          let className = 'alphabet-letter';
          if (isCorrect) className += ' correct';
          else if (isIncorrect) className += ' incorrect';
          else if (isGuessed) className += ' guessed';
          
          return (
            <span key={letter} className={className}>
              {letter.toUpperCase()}
            </span>
          );
        })}
      </div>
    );
  };

  return (
    <div className="container">
      <header className="header">
        <h1>🎯 Hangman Game</h1>
        <p>Guess the word one letter at a time!</p>
      </header>

      {/* Game Statistics */}
      {stats && (
        <div className="stats-bar">
          <h3>📊 Your Stats</h3>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-value">{stats.total_games}</span>
              <span className="stat-label">Games Played</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{stats.won_games}</span>
              <span className="stat-label">Wins</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{stats.win_rate}%</span>
              <span className="stat-label">Win Rate</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{stats.active_games}</span>
              <span className="stat-label">Active</span>
            </div>
          </div>
        </div>
      )}

      {/* Game Controls */}
      <div className="game-controls">
        <button 
          className="btn btn-primary"
          onClick={initGameData}
          disabled={loading}
        >
          {loading ? 'Loading...' : '🎮 Initialize Game Data'}
        </button>
        
        <button 
          className="btn btn-success"
          onClick={startNewGame}
          disabled={loading}
        >
          {loading ? 'Loading...' : '🆕 New Game'}
        </button>
        
        <button 
          className="btn btn-warning"
          onClick={loadCurrentGame}
          disabled={loading}
        >
          {loading ? 'Loading...' : '🔄 Load Current Game'}
        </button>
      </div>

      {/* Message Display */}
      {message && (
        <div className={`message ${gameState?.status === 'won' ? 'success' : gameState?.status === 'lost' ? 'error' : ''}`}>
          {message}
        </div>
      )}

      {/* Game Board */}
      {gameState && (
        <div className="game-board">
          {/* Hangman Drawing */}
          <div className="hangman-container">
            <h3>Hangman</h3>
            <pre className="hangman-drawing">
              {renderHangman(gameState.attempts_left, gameState.max_attempts)}
            </pre>
            <p className="attempts-info">
              Attempts left: <strong>{gameState.attempts_left}/{gameState.max_attempts}</strong>
            </p>
          </div>

          {/* Word Progress */}
          <div className="word-container">
            <h3>Word Progress</h3>
            <div className="word-display">
              {gameState.word_progress}
            </div>
            <p className="word-info">
              Length: {gameState.word_length} letters
              {gameState.word_revealed && (
                <span className="word-revealed">
                  <br/>Word: <strong>{gameState.word_revealed}</strong>
                </span>
              )}
            </p>
            
            {/* Game Status */}
            <div className={`game-status status-${gameState.status}`}>
              Status: {gameState.status.toUpperCase()}
              {gameState.status === 'won' && ' 🎉'}
              {gameState.status === 'lost' && ' 💀'}
            </div>
          </div>
        </div>
      )}

      {/* Guess Input */}
      {gameState && gameState.status === 'active' && (
        <div className="guess-container">
          <h3>Make Your Guess</h3>
          <div className="guess-input-group">
            <input
              type="text"
              className="guess-input"
              placeholder="Enter a letter"
              value={guessInput}
              onChange={(e) => setGuessInput(e.target.value)}
              onKeyPress={handleKeyPress}
              maxLength={1}
              disabled={loading}
            />
            <button
              className="btn btn-primary"
              onClick={makeGuess}
              disabled={loading || !guessInput.trim()}
            >
              {loading ? 'Guessing...' : 'Guess!'}
            </button>
          </div>
        </div>
      )}

      {/* Alphabet Visual */}
      {gameState && (
        <div className="alphabet-container">
          <h3>Letters</h3>
          {renderAlphabet()}
          <div className="legend">
            <span className="legend-item">
              <span className="alphabet-letter correct">A</span> Correct
            </span>
            <span className="legend-item">
              <span className="alphabet-letter incorrect">B</span> Incorrect
            </span>
            <span className="legend-item">
              <span className="alphabet-letter">C</span> Not Guessed
            </span>
          </div>
        </div>
      )}

      {/* Guessed Letters Display */}
      {gameState && (gameState.guessed_letters.length > 0) && (
        <div className="guessed-letters">
          <div className="letters-section">
            <h4>✅ Correct Letters</h4>
            <div className="letters-display">
              {gameState.correct_letters.length > 0 
                ? gameState.correct_letters.map(letter => letter.toUpperCase()).join(', ')
                : 'None yet'
              }
            </div>
          </div>
          <div className="letters-section">
            <h4>❌ Incorrect Letters</h4>
            <div className="letters-display">
              {gameState.incorrect_letters.length > 0
                ? gameState.incorrect_letters.map(letter => letter.toUpperCase()).join(', ')
                : 'None yet'
              }
            </div>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="instructions">
        <h3>How to Play</h3>
        <ol>
          <li>Click "🎮 Initialize Game Data" first (only needed once)</li>
          <li>Click "🆕 New Game" to start a fresh game</li>
          <li>Guess letters one at a time to reveal the word</li>
          <li>You have 6 wrong guesses before the game ends</li>
          <li>Win by guessing all letters in the word!</li>
        </ol>
      </div>
    </div>
  );
}

export default App;