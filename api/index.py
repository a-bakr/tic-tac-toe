from tic_tac_toe import State, Player, BOARD_ROWS, BOARD_COLS, all_states
from flask import Flask, render_template, jsonify, request
import numpy as np
import os

app = Flask(__name__)

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

game = GameState()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reset', methods=['POST'])
def reset():
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
    
    return jsonify({
        'board': game.state.data.tolist(),
        'gameOver': game.game_over,
        'winner': game.winner,
        'humanGoesFirst': game.human_goes_first,
        'aiMove': {'row': i, 'col': j} if not game.human_goes_first else None
    })

@app.route('/play', methods=['POST'])
def play():
    if game.game_over:
        return jsonify({
            'board': game.state.data.tolist(),
            'gameOver': game.game_over,
            'winner': game.winner,
            'message': 'Game is already over',
            'humanGoesFirst': game.human_goes_first
        })
    
    data = request.get_json()
    row = data.get('row')
    col = data.get('col')
    
    # Check if the move is valid
    if game.state.data[row, col] != 0:
        return jsonify({
            'board': game.state.data.tolist(),
            'gameOver': game.game_over,
            'winner': game.winner,
            'message': 'Invalid move',
            'humanGoesFirst': game.human_goes_first
        })
    
    # Human player move - symbol is 1 if human goes first, -1 if second
    human_symbol = 1 if game.human_goes_first else -1
    game.state = game.state.next_state(row, col, human_symbol)
    game.current_ai.set_state(game.state)
    
    # Check if game is over after human move
    if game.state.is_end():
        game.game_over = True
        game.winner = game.state.winner
        return jsonify({
            'board': game.state.data.tolist(),
            'gameOver': game.game_over,
            'winner': game.winner,
            'humanGoesFirst': game.human_goes_first
        })
    
    # AI player move
    game.current_ai.set_state(game.state)
    i, j, symbol = game.current_ai.act()
    game.state = game.state.next_state(i, j, symbol)
    
    # Check if game is over after AI move
    if game.state.is_end():
        game.game_over = True
        game.winner = game.state.winner
    
    return jsonify({
        'board': game.state.data.tolist(),
        'gameOver': game.game_over,
        'winner': game.winner,
        'aiMove': {'row': i, 'col': j},
        'humanGoesFirst': game.human_goes_first
    })

if __name__ == '__main__':
    app.run(debug=True) 