from pieces import Piece, Pawn, Rook, Knight, Bishop, Queen, King
from cells import ChessCell


class ChessGame:
    def __init__(self, max_turns, player_color):
        self.max_turns = max_turns
        self.turn_count = 0
        # Modify initial current_player based on player's color choice
        self.current_player = 2 if player_color == "black" else 1
        self.player_color = player_color
        self.board_status = self.initialize_pieces()
        self.board_size = 8


    def __str__(self) -> str:
        board_repr = ""
        bottom_row = " "
        for j in range(1, self.board_size + 1):
            cur_row = f"{j}  "
            for i in range(1, self.board_size + 1):
                letter = ChessCell.index_to_letter[i]
                if j == 1:
                    bottom_row += f" {letter}"
                pos = f"{letter}{j}"
                piece = self.board_status.get(pos)
                if piece is None:
                    cur_row += " ·"
                else:
                    cur_row += f" {piece.symbol}"
            board_repr = f"{cur_row}\n" + board_repr
        return board_repr + f"  {bottom_row}"




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
        if self.player_color == "white":
            # If player is white, 1 is white, 2 is black
            current_player_color = "white" if self.current_player == 1 else "black"
        else:
            # If player is black, 1 is black, 2 is white
            current_player_color = "black" if self.current_player == 1 else "white"

        if piece.color.lower() != current_player_color:
            print(f"Player {self.current_player} can only move {current_player_color} pieces!")
            return False

        # Validate piece movement
        # trajectory = piece.move(
        # if trajectory is not None
        # controlla se la traiettoria e libera se il pezzo non e un cavallo
        if not piece.move(start_cell, end_cell):
            print(f"Invalid move for {piece}!")
            return False

        #is_valid = self.validate_move(piece, start_cell, end_cell, trajectory)

        # Move the piece
        self.board_status[end_cell_str] = piece
        del self.board_status[start_cell_str]

        piece.moved(start_cell, end_cell)
        print(f"Player {self.current_player} plays: {move}")
        print(str(self))
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


# Define games dictionary after ChessGame class
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
        self.players = {}

    def ask_user(self):
        # Which game?
        game = input("Which game? (chess): ").strip().lower()
        if game in games:
            turns_input = input("How many turns? ")

            # Validate turns input
            if not turns_input.isnumeric():
                print("Not a valid amount of turns!")
                return False

            turns = int(turns_input)

            # Check if turns are within acceptable range
            if turns > 50:
                print("Not a valid amount of turns!")
                return False

            color_choice = input("Do you want to be White or Black? ").strip().lower()
            if color_choice in player_color:
                self.players[1] = color_choice
                self.players[2] = "black" if color_choice == "white" else "white"
                self.game = games[game](turns, color_choice)
                self.player_interactor = PlayerInteractor()
                return True
            else:
                print("Color not recognized!")
                return False
        else:
            print("Game not recognized!")
            return False

    def play(self):
        # Only start the game if ask_user() was successful
        if self.game is None:
            print("Please start a valid game first.")
            return

        turn_count = 1
        print(str(self.game))
        while turn_count < self.game.max_turns:
            print(f"\n--- Turn {turn_count} ---")
            move = self.player_interactor.interact(self.game.current_player)
            if self.game.play_move(move):
                turn_count += 1
        print("Game over after", self.game.max_turns, "turns")


# Start game
if __name__ == "__main__":
    controller = GameController()
    if controller.ask_user():
        controller.play()