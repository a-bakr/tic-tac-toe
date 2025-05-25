from api.tic_tac_toe import State, Player, BOARD_ROWS, BOARD_COLS, all_states
from fastapi import FastAPI, Request, Body, Depends, Cookie, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# Set up templates and static files
app.mount("/static", StaticFiles(directory="api/static"), name="static")
templates = Jinja2Templates(directory="api/templates")

class PlayRequest(BaseModel):
    row: int
    col: int

class GameState:
    def __init__(self):
        self.state = State()
        # Create two AI players for different roles
        self.ai_player_first = Player(epsilon=0)
        self.ai_player_first.set_symbol(1)  # AI as 'X' (first player)
        
        self.ai_player_second = Player(epsilon=0)
        self.ai_player_second.set_symbol(-1)  # AI as 'O' (second player)
        
        # Load AI policies if they exist
        try:
            self.ai_player_first.load_policy()
            self.ai_player_second.load_policy()
        except:
            print("No policy file found. AI will play randomly.")
        
        self.human_goes_first = True  # Default: human goes first
        self.current_ai = self.ai_player_second  # Default AI player (second)
        self.game_over = False
        self.winner = None
        self.waiting_for_ai_first_move = False

# Store active games
active_games = {}

# Helper function to get or create a game for a session
async def get_game_state(request: Request) -> GameState:
    session_id = request.session.get("session_id")
    
    # Create new session if needed
    if not session_id or session_id not in active_games:
        session_id = str(uuid.uuid4())
        request.session["session_id"] = session_id
        active_games[session_id] = GameState()
    
    return active_games[session_id]

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Ensure user has a game state
    await get_game_state(request)
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/reset")
async def reset(request: Request):
    game = await get_game_state(request)
    
    # Toggle who goes first
    game.human_goes_first = not game.human_goes_first
    
    # Reset the game state
    game.state = State()
    game.game_over = False
    game.winner = None
    
    # Choose the appropriate AI based on who goes first
    if game.human_goes_first:
        game.current_ai = game.ai_player_second
        game.waiting_for_ai_first_move = False
        return {
            'board': game.state.data.tolist(),
            'gameOver': game.game_over,
            'winner': game.winner,
            'humanGoesFirst': game.human_goes_first,
            'aiMove': None
        }
    else:
        game.current_ai = game.ai_player_first
        game.waiting_for_ai_first_move = True
        
        # If AI goes first, make its move immediately
        game.current_ai.set_state(game.state)
        i, j, symbol = game.current_ai.act()
        game.state = game.state.next_state(i, j, symbol)
        
        # Check if game is over after AI move (unlikely on first move)
        if game.state.is_end():
            game.game_over = True
            game.winner = game.state.winner
        
        return {
            'board': game.state.data.tolist(),
            'gameOver': game.game_over,
            'winner': game.winner,
            'humanGoesFirst': game.human_goes_first,
            'aiMove': {'row': i, 'col': j}
        }

@app.post("/play")
async def play(move: PlayRequest, request: Request):
    game = await get_game_state(request)
    
    if game.game_over:
        return {
            'board': game.state.data.tolist(),
            'gameOver': game.game_over,
            'winner': game.winner,
            'message': 'Game is already over',
            'humanGoesFirst': game.human_goes_first
        }
    
    row = move.row
    col = move.col
    
    # Check if the move is valid
    if game.state.data[row, col] != 0:
        return {
            'board': game.state.data.tolist(),
            'gameOver': game.game_over,
            'winner': game.winner,
            'message': 'Invalid move',
            'humanGoesFirst': game.human_goes_first
        }
    
    # Human player move - symbol is 1 if human goes first, -1 if second
    human_symbol = 1 if game.human_goes_first else -1
    game.state = game.state.next_state(row, col, human_symbol)
    game.current_ai.set_state(game.state)
    
    # Check if game is over after human move
    if game.state.is_end():
        game.game_over = True
        game.winner = game.state.winner
        return {
            'board': game.state.data.tolist(),
            'gameOver': game.game_over,
            'winner': game.winner,
            'humanGoesFirst': game.human_goes_first
        }
    
    # AI player move
    game.current_ai.set_state(game.state)
    i, j, symbol = game.current_ai.act()
    game.state = game.state.next_state(i, j, symbol)
    
    # Check if game is over after AI move
    if game.state.is_end():
        game.game_over = True
        game.winner = game.state.winner
    
    return {
        'board': game.state.data.tolist(),
        'gameOver': game.game_over,
        'winner': game.winner,
        'aiMove': {'row': i, 'col': j},
        'humanGoesFirst': game.human_goes_first
    }

# Cleanup route for inactive games (optional)
@app.get("/api/cleanup")
async def cleanup_inactive_games():
    # In a real app, you'd check timestamps and clear old games
    count = len(active_games)
    return {"message": f"Currently {count} active games"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True) 