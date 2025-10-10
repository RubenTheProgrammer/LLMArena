from copy import deepcopy
from ..base import Game


class TicTacToeGame(Game):
    def __init__(self, max_turns, player_color):
        super().__init__(
            max_turns=max_turns,
            player_color=player_color,
            board_size=3,
        )
        if player_color == "x":
            self.current_player = 1
        else:
            self.current_player = 2

    @classmethod
    def get_player_types(cls):
        from . import TicTacToeAIPlayer, TicTacToeHumanPlayer

        return {
            "ai": TicTacToeAIPlayer,
            "human": TicTacToeHumanPlayer,
        }

    @classmethod
    def get_default_colors(cls):
        return ["x", "o"]

    def __str__(self) -> str:
        board_repr = ""
        bottom_row = " "
        letters = ["a", "b", "c"]

        for j in range(3, 0, -1):
            cur_row = f"{j}  "
            for i in range(1, 4):
                letter = letters[i - 1]
                if j == 1:
                    bottom_row += f" {letter}"
                pos = f"{letter}{j}"
                piece = self.board_status.get(pos)
                if piece is None:
                    cur_row += " ·"
                else:
                    cur_row += f" {piece}"
            board_repr += f"{cur_row}\n"
        return board_repr + f"  {bottom_row}"

    def initialize_game(self):
        return {}

    def log_move(self, position, symbol):
        self.gamelog.append(f"{symbol}{position}")

    def play_move(self, move):
        if not self._validate_move_format(move):
            print(f"Move '{move}' is not valid format!")
            return False

        if move in self.board_status:
            print(f"Position {move} is already occupied!")
            return False

        current_symbol = "x" if self.current_player == 1 and self.player_color == "x" else "o"
        current_symbol = "o" if self.current_player == 1 and self.player_color == "o" else current_symbol
        current_symbol = "x" if self.current_player == 2 and self.player_color == "o" else current_symbol
        current_symbol = "o" if self.current_player == 2 and self.player_color == "x" else current_symbol

        self.board_status[move] = current_symbol.upper()
        self.log_move(move, current_symbol.upper())

        print(f"Player {self.current_player} plays: {move}")
        print(str(self))

        if self._check_win(current_symbol.upper()):
            self.winner = self.current_player
            self.game_over = True
            print(f"Player {self.current_player} ({current_symbol.upper()}) wins!")
            return "win"

        if len(self.board_status) == 9:
            self.game_over = True
            print("Game is a draw!")
            return True

        self.turn_count += 1
        self.current_player = 2 if self.current_player == 1 else 1

        return True

    def _validate_move_format(self, move):
        if len(move) != 2:
            return False

        if move[0] not in 'abc' or move[1] not in '123':
            return False

        return True

    def _check_win(self, symbol):
        winning_combinations = [
            ["a1", "a2", "a3"],
            ["b1", "b2", "b3"],
            ["c1", "c2", "c3"],
            ["a1", "b1", "c1"],
            ["a2", "b2", "c2"],
            ["a3", "b3", "c3"],
            ["a1", "b2", "c3"],
            ["a3", "b2", "c1"]
        ]

        for combo in winning_combinations:
            if all(self.board_status.get(pos) == symbol for pos in combo):
                return True

        return False