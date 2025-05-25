# Tic Tac Toe vs AI

A modern web application that allows you to play Tic Tac Toe against an AI opponent trained using reinforcement learning.

## Features

- Clean, modern UI
- Responsive design that works on desktop and mobile
- Play against an AI that has learned optimal strategies
- Players alternate going first with each new game
- Visual feedback for game state and moves

## Requirements

- Python 3.6+
- Flask
- NumPy

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install flask numpy
```

## Running the Application

1. Make sure the AI policy files are available in the `policy` directory. If not, you can train the AI by running:

```bash
python tic_tac_toe.py
```

2. Start the web application:

```bash
python api/index.py
```

3. Open your web browser and navigate to `http://localhost:5000`

## How to Play

- Players alternate who goes first with each new game
- X always goes first, O always goes second
- Click on any empty cell to make your move
- The AI will automatically respond with its move
- The game will indicate when someone wins or if there's a draw
- Click the "New Game" button to start a new game and switch who goes first

## Game Logic

The AI uses reinforcement learning techniques to learn optimal play strategies. The backend is written in Python, while the frontend uses HTML, CSS, and JavaScript to provide a responsive and interactive gaming experience.

## Credits

This application combines a reinforcement learning Tic Tac Toe implementation with a modern web interface.

## License

MIT 