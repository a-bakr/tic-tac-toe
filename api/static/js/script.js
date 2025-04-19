document.addEventListener("DOMContentLoaded", () => {
	const board = document.getElementById("board");
	const resetBtn = document.getElementById("resetBtn");
	const statusDisplay = document.getElementById("status");
	const soundToggleBtn = document.getElementById("soundToggleBtn");

	// Sound effects
	const moveSound = new Audio("/static/sounds/move.mp3");

	// Remove sound toggle button from DOM
	if (soundToggleBtn) {
		soundToggleBtn.style.display = "none";
	}

	let gameState = {
		board: Array(3)
			.fill()
			.map(() => Array(3).fill(0)),
		gameOver: false,
		winner: null,
		humanGoesFirst: true,
	};

	// Disable board input (when it's AI's turn)
	function disableBoardInput() {
		board.classList.add("disabled");
	}

	// Enable board input (when it's human's turn)
	function enableBoardInput() {
		board.classList.remove("disabled");
	}

	// Initialize the game
	function initGame() {
		// Create the board cells
		board.innerHTML = "";
		for (let i = 0; i < 3; i++) {
			for (let j = 0; j < 3; j++) {
				const cell = document.createElement("div");
				cell.classList.add("cell");
				cell.dataset.row = i;
				cell.dataset.col = j;
				cell.addEventListener("click", () => makeMove(i, j));
				board.appendChild(cell);
			}
		}

		// Reset game state
		resetGame();
	}

	// Reset the game
	function resetGame() {
		// Disable board input during reset
		disableBoardInput();

		fetch("/reset", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
		})
			.then((response) => response.json())
			.then((data) => {
				// Store AI move if AI goes first
				const aiMove = data.aiMove;

				// If AI goes first, temporarily hide its move
				if (aiMove) {
					const aiSymbol = data.humanGoesFirst ? -1 : 1;
					data.board[aiMove.row][aiMove.col] = 0;
				}

				// Update game state and board without AI's move
				gameState = data;
				updateBoard();

				// Update the turn status
				updateTurnStatus();

				// If AI made a first move, add it after a delay
				if (aiMove) {
					// Set status to show it's user's turn with the correct symbol
					if (!gameState.humanGoesFirst) {
						const symbol = "X";
						statusDisplay.textContent = `Your turn (${symbol})`;
						statusDisplay.className = "status";
					}

					setTimeout(() => {
						// Apply AI's move to the board
						const aiSymbol = gameState.humanGoesFirst ? -1 : 1;
						gameState.board[aiMove.row][aiMove.col] = aiSymbol;
						updateBoard();
						highlightCell(aiMove.row, aiMove.col);

						// Play move sound for AI's first move
						moveSound.play();

						// Enable board input for human's turn
						enableBoardInput();
					}, 1000);
				} else {
					// Human goes first, enable board input
					enableBoardInput();
				}
			})
			.catch((error) => console.error("Error:", error));
	}

	// Make a move
	function makeMove(row, col) {
		// Check if the game is over or the cell is already taken
		if (gameState.gameOver || gameState.board[row][col] !== 0) {
			return;
		}

		// Play move sound for human move
		moveSound.play();

		// Disable board input immediately after human makes a move
		disableBoardInput();

		// Send the move to the server
		fetch("/play", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({ row, col }),
		})
			.then((response) => response.json())
			.then((data) => {
				// Store AI move but don't apply it yet
				const aiMove = data.aiMove;

				// Create a temporary game state without the AI move
				const tempGameState = JSON.parse(JSON.stringify(data));

				// If AI made a move, temporarily remove it from the board
				if (aiMove) {
					const aiSymbol = gameState.humanGoesFirst ? -1 : 1;
					tempGameState.board[aiMove.row][aiMove.col] = 0;
				}

				// Update game state and board without AI's move
				gameState = tempGameState;
				updateBoard();

				// Update status to show AI is thinking
				const aiSymbol = gameState.humanGoesFirst ? "O" : "X";
				statusDisplay.textContent = `AI is thinking (${aiSymbol})...`;

				// Add 1 second delay before showing the AI's move
				setTimeout(() => {
					// Apply AI's move to the game state
					if (aiMove) {
						const aiSymbol = gameState.humanGoesFirst ? -1 : 1;
						gameState.board[aiMove.row][aiMove.col] = aiSymbol;
						updateBoard();
						highlightCell(aiMove.row, aiMove.col);

						// Play move sound for AI move
						moveSound.play();
					}

					updateGameStatus();

					// Re-enable board input if game isn't over
					if (!gameState.gameOver) {
						enableBoardInput();
					}
				}, 1000);
			})
			.catch((error) => console.error("Error:", error));
	}

	// Highlight a cell temporarily
	function highlightCell(row, col) {
		const cells = document.querySelectorAll(".cell");
		const cell = [...cells].find(
			(cell) => parseInt(cell.dataset.row) === row && parseInt(cell.dataset.col) === col
		);

		if (cell) {
			cell.classList.add("highlight");
			setTimeout(() => {
				cell.classList.remove("highlight");
			}, 1000);
		}
	}

	// Update the board based on the current game state
	function updateBoard() {
		const cells = document.querySelectorAll(".cell");
		cells.forEach((cell) => {
			const row = parseInt(cell.dataset.row);
			const col = parseInt(cell.dataset.col);
			const value = gameState.board[row][col];

			// Clear existing classes
			cell.classList.remove("x", "o");

			// Set content based on value
			if (value === 1) {
				cell.classList.add(gameState.humanGoesFirst ? "x" : "o");
				cell.innerHTML = gameState.humanGoesFirst
					? '<i class="fas fa-times"></i>'
					: '<i class="fas fa-circle"></i>';
			} else if (value === -1) {
				cell.classList.add(gameState.humanGoesFirst ? "o" : "x");
				cell.innerHTML = gameState.humanGoesFirst
					? '<i class="fas fa-circle"></i>'
					: '<i class="fas fa-times"></i>';
			} else {
				cell.innerHTML = "";
			}
		});
	}

	// Update turn status
	function updateTurnStatus() {
		if (gameState.gameOver) {
			updateGameStatus();
		} else {
			const isHumanTurn =
				(gameState.humanGoesFirst && countMoves() % 2 === 0) ||
				(!gameState.humanGoesFirst && countMoves() % 2 === 1);

			if (isHumanTurn) {
				const symbol = gameState.humanGoesFirst ? "X" : "O";
				statusDisplay.textContent = `Your turn (${symbol})`;
				statusDisplay.className = "status";
			} else {
				const symbol = gameState.humanGoesFirst ? "O" : "X";
				statusDisplay.textContent = `AI's turn (${symbol})`;
				statusDisplay.className = "status";
			}
		}
	}

	// Count total moves made
	function countMoves() {
		return gameState.board.flat().filter((cell) => cell !== 0).length;
	}

	// Update game status
	function updateGameStatus() {
		if (gameState.gameOver) {
			if (gameState.winner === (gameState.humanGoesFirst ? 1 : -1)) {
				statusDisplay.textContent = "You win!";
				statusDisplay.className = "status win";
			} else if (gameState.winner === (gameState.humanGoesFirst ? -1 : 1)) {
				statusDisplay.textContent = "AI wins!";
				statusDisplay.className = "status lose";
			} else {
				statusDisplay.textContent = "It's a draw!";
				statusDisplay.className = "status draw";
			}
		} else {
			updateTurnStatus();
		}
	}

	// Event listener for reset button
	resetBtn.addEventListener("click", resetGame);

	// Initialize the game
	initGame();
});
