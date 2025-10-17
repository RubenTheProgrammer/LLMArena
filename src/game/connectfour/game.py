from copy import deepcopy
from ..base import Game


class ConnectFourGame(Game):
    def __init__(self, max_turns, player_color):
        super().__init__(
            max_turns=max_turns,
            player_color=player_color,
            board_size=(7, 6),
        )
        self.columns = 7
        self.rows = 6
        self.board = [[None for _ in range(self.columns)] for _ in range(self.rows)]

        if player_color == "red":
            self.current_player = 1
        else:
            self.current_player = 2

    @classmethod
    def get_player_types(cls):
        from . import ConnectFourAIPlayer, ConnectFourHumanPlayer

        return {
            "ai": ConnectFourAIPlayer,
            "human": ConnectFourHumanPlayer,
        }

    @classmethod
    def get_default_colors(cls):
        return ["red", "yellow"]

    def __str__(self) -> str:
        board_repr = ""

        for row in range(self.rows):
            cur_row = ""
            for col in range(self.columns):
                piece = self.board[row][col]
                if piece is None:
                    cur_row += " ·"
                elif piece == "R":
                    cur_row += " R"
                else:
                    cur_row += " Y"
            board_repr += f"{cur_row}\n"

        board_repr += " 1 2 3 4 5 6 7"
        return board_repr

    def initialize_game(self):
        return {}

    def log_move(self, column, symbol):
        self.gamelog.append(f"{symbol}{column}")

    def play_move(self, move):
        if not self._validate_move_format(move):
            print(f"Move '{move}' is not valid format!")
            return False

        column = int(move) - 1

        if column < 0 or column >= self.columns:
            print(f"Column {move} is out of range!")
            return False

        if self.board[0][column] is not None:
            print(f"Column {move} is full!")
            return False

        current_symbol = "R" if self.current_player == 1 and self.player_color == "red" else "Y"
        current_symbol = "Y" if self.current_player == 1 and self.player_color == "yellow" else current_symbol
        current_symbol = "R" if self.current_player == 2 and self.player_color == "yellow" else current_symbol
        current_symbol = "Y" if self.current_player == 2 and self.player_color == "red" else current_symbol

        row = self._drop_piece(column, current_symbol)
        self.log_move(move, current_symbol)

        print(f"Player {self.current_player} plays: Column {move}")
        print(str(self))

        if self._check_win(row, column, current_symbol):
            self.winner = self.current_player
            self.game_over = True
            color_name = "Red" if current_symbol == "R" else "Yellow"
            print(f"Player {self.current_player} ({color_name}) wins!")
            return "win"

        if self._is_board_full():
            self.game_over = True
            print("Game is a draw!")
            return True

        self.turn_count += 1
        self.current_player = 2 if self.current_player == 1 else 1

        return True

    def _validate_move_format(self, move):
        if not move.isdigit():
            return False

        column = int(move)
        if column < 1 or column > 7:
            return False

        return True

    def _drop_piece(self, column, symbol):
        for row in range(self.rows - 1, -1, -1):
            if self.board[row][column] is None:
                self.board[row][column] = symbol
                return row
        return -1

    def _is_board_full(self):
        for col in range(self.columns):
            if self.board[0][col] is None:
                return False
        return True

    def _check_win(self, row, col, symbol):
        directions = [
            (0, 1),
            (1, 0),
            (1, 1),
            (1, -1)
        ]

        for dr, dc in directions:
            count = 1

            for i in range(1, 4):
                r, c = row + dr * i, col + dc * i
                if 0 <= r < self.rows and 0 <= c < self.columns and self.board[r][c] == symbol:
                    count += 1
                else:
                    break

            for i in range(1, 4):
                r, c = row - dr * i, col - dc * i
                if 0 <= r < self.rows and 0 <= c < self.columns and self.board[r][c] == symbol:
                    count += 1
                else:
                    break

            if count >= 4:
                return True

        return False