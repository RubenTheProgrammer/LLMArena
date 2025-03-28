from pieces import Piece, Pawn, Rook, Knight, Bishop, Queen, King
from cells import ChessCell


class ChessGame:
    def __init__(self, max_turns, player_color):
        self.max_turns = max_turns
        self.turn_count = 0
        self.current_player = 1  # 1 = white, 2 = black
        self.player_color = player_color
        self.board_status = self.initialize_pieces()

    def initialize_pieces(self):
        # Using the actual piece classes from pieces.py
        pieces = {
            "a1": Rook("white"), "b1": Knight("white"), "c1": Bishop("white"),
            "d1": Queen("white"), "e1": King("white"), "f1": Bishop("white"),
            "g1": Knight("white"), "h1": Rook("white"),
            "a2": Pawn("white"), "b2": Pawn("white"), "c2": Pawn("white"),
            "d2": Pawn("white"), "e2": Pawn("white"), "f2": Pawn("white"),
            "g2": Pawn("white"), "h2": Pawn("white"),

            "a7": Pawn("black"), "b7": Pawn("black"), "c7": Pawn("black"),
            "d7": Pawn("black"), "e7": Pawn("black"), "f7": Pawn("black"),
            "g7": Pawn("black"), "h7": Pawn("black"),
            "a8": Rook("black"), "b8": Knight("black"), "c8": Bishop("black"),
            "d8": Queen("black"), "e8": King("black"), "f8": Bishop("black"),
            "g8": Knight("black"), "h8": Rook("black")
        }
        return pieces

    def play_move(self, move):
        # More robust move validation
        if not self._validate_move_format(move):
            print(f"Move '{move}' is not valid!")
            return False

        # Parse move
        start_cell_str, end_cell_str = move.split('-')
        start_cell = ChessCell(start_cell_str)
        end_cell = ChessCell(end_cell_str)

        # Check if a piece exists at the start cell
        if start_cell_str not in self.board_status:
            print(f"No piece at {start_cell_str}!")
            return False

        piece = self.board_status[start_cell_str]

        # Validate piece color matches current player
        current_player_color = "white" if self.current_player == 1 else "black"
        if piece.color.lower() != current_player_color:
            print(f"You can only move {current_player_color} pieces!")
            return False

        # Validate piece movement
        if not piece.move(start_cell, end_cell):
            print(f"Invalid move for {piece}!")
            return False

        # Move the piece
        self.board_status[end_cell_str] = piece
        del self.board_status[start_cell_str]

        print(f"Player {self.current_player} plays: {move}")
        self.turn_count += 1
        self.current_player = 2 if self.current_player == 1 else 1
        return True

    def _validate_move_format(self, move):
        # Validate move format
        if len(move) != 5 or move[2] != '-':
            return False

        start_cell, end_cell = move.split('-')

        # Validate cell format
        if (len(start_cell) != 2 or len(end_cell) != 2 or
                start_cell[0] not in 'abcdefgh' or end_cell[0] not in 'abcdefgh' or
                not start_cell[1].isdigit() or not end_cell[1].isdigit() or
                int(start_cell[1]) < 1 or int(start_cell[1]) > 8 or
                int(end_cell[1]) < 1 or int(end_cell[1]) > 8):
            return False

        return True


# Game setup and controller remain the same
games = {"chess": ChessGame}
player_color = ["white", "black"]


class PlayerInteractor:
    def interact(self, player):
        move = input(f"Player {player}, enter your move (e.g., 'e2-e4'): ")
        return move


class GameController:
    def __init__(self):
        self.game = None
        self.player_interactor = None
        self.players = {1: None, 2: None}

    def ask_user(self):
        # Which game?
        game = input("Which game? (chess): ").strip().lower()
        if game in games:
            turns = int(input("How many turns? "))
            color_choice = input("Do you want to be White or Black? ").strip().lower()
            if color_choice in player_color:
                self.players[1] = color_choice
                self.players[2] = "black" if color_choice == "white" else "white"
                self.game = games[game](turns, color_choice)
                self.player_interactor = PlayerInteractor()
            else:
                print("Color not recognized!")
        else:
            print("Game not recognized!")

    def play(self):
        turn_count = 1
        while turn_count < self.game.max_turns:
            print(f"\n--- Turn {turn_count} ---")
            move = self.player_interactor.interact(self.game.current_player)
            if self.game.play_move(move):
                turn_count += 1
        print("Game over after", self.game.max_turns, "turns")


# Start game
if __name__ == "__main__":
    controller = GameController()
    controller.ask_user()
    controller.play()