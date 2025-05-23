from ollama import chat
import json


class Player:
    # Base class for all players

    def __init__(self, player_number, color):
        self.player_number = player_number
        self.color = color

    def get_move(self, board_status):
        raise NotImplementedError

    def notify_move(self, move, board_status):
        pass


class HumanPlayer(Player):
    # human player input is from console

    def get_move(self, board_status):
        move = input(f"Player {self.player_number} ({self.color}), enter your move (e.g., 'e2-e4'): ")
        return move


class AIPlayer(Player):
    # AI player uses ollama for moves

    def __init__(self, player_number, color):
        super().__init__(player_number, color)
        self.prompt_format = """
        You are playing chess as the {color} pieces. 

        Current board state:
        {board_status}

        IMPORTANT: 
        1. Look CAREFULLY at the current board state above and identify which pieces are on which squares.
        2. Only select a piece that currently exists on the board.
        3. Verify that the start position you choose actually has one of your {color} pieces on it.
        4. The board changes after each move, so never assume a piece is at its starting position.

        Chess pieces are represented as:
        - Pawns: ♙ (white) ♟ (black)
        - Rooks: ♖ (white) ♜ (black) 
        - Knights: ♘ (white) ♞ (black)
        - Bishops: ♗ (white) ♝ (black)
        - Queens: ♕ (white) ♛ (black)
        - Kings: ♔ (white) ♚ (black)
        - Empty squares: · (dot)

        Make your next move. Your move must be:
        1. A valid chess move for your {color} pieces on the CURRENT board
        2. In the format "start-end" (e.g., "e2-e4")
        3. Using algebraic notation (a-h for columns, 1-8 for rows)

        Remember standard chess rules:
        - Pawns move forward 1 space (2 on first move) and capture diagonally
        - Rooks move horizontally or vertically
        - Knights move in an L-shape (2 spaces one way, 1 space perpendicular)
        - Bishops move diagonally
        - Queens move horizontally, vertically, or diagonally
        - Kings move 1 space in any direction
        - You cannot move through occupied spaces (except knights)
        - You cannot capture your own pieces

        Before responding:
        1. DOUBLE-CHECK that your chosen start position actually has one of your pieces
        2. VERIFY that the move is legal according to chess rules
        3. ENSURE your response is in the exact format requested

        Respond ONLY with the move in JSON format with 'start' and 'end' fields.
        """
        self.response_schema = {
            "type": "object",
            "properties": {
                "start": {
                    "description": "the current position of the piece to move (must have your piece on it)",
                    "type": "string",
                    "pattern": "^[a-h][1-8]$"
                },
                "end": {
                    "description": "the end position of the move",
                    "type": "string",
                    "pattern": "^[a-h][1-8]$"
                }
            },
            "required": [
                "start",
                "end",
            ]
        }
        self.model = "llama3.2"
        self.game = None  # Will be set by GameController

    def get_move(self, board_status):
        print(f"AI Player {self.player_number} ({self.color}) is thinking...")

        # Get the visual board representation
        board_visual = str(self.game)

        response = chat(
            model=self.model,
            messages=[{'role': 'user',
                       'content': self.prompt_format.format(color=self.color, board_status=board_visual)}],
            format=self.response_schema,
            stream=False,
        )
        content = json.loads(response.message.content)
        return content["start"] + "-" + content["end"]