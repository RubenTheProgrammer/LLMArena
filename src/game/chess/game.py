from copy import deepcopy

from .cells import ChessCell
from .pieces import Pawn, Rook, Knight, Bishop, Queen, King
from ..base import Game


class ChessGame(Game):
    def __init__(self, max_turns, player_color):
        super().__init__(
            max_turns=max_turns,
            player_color=player_color,
            board_size=8,
        )
        self.captured_pieces = {"white": [], "black": []}

    @classmethod
    def get_player_types(cls):
        return {
            "ai": "MoveslogAiplayer"
        }

    @classmethod
    def get_default_colors(cls):
        return ["white", "black"]

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

    def initialize_game(self):
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

    def log_move(self, piece, end_cell):
        if isinstance(piece, Pawn):
            piece_initial = ""
        else:
            piece_initial = piece.piece_initial

        self.gamelog.append(piece_initial + str(end_cell))

    def play_move(self, move):
        if not self._validate_move_format(move):
            print(f"Move '{move}' is not valid!")
            return False

        start_cell_str, end_cell_str = move.split('-')
        start_cell = ChessCell(start_cell_str)
        end_cell = ChessCell(end_cell_str)

        if start_cell_str not in self.board_status:
            print(f"No piece at {start_cell_str}!")
            return False

        piece = self.board_status[start_cell_str]

        if self.player_color == "white":
            current_player_color = "white" if self.current_player == 1 else "black"
        else:
            current_player_color = "black" if self.current_player == 1 else "white"

        if piece.color.lower() != current_player_color:
            print(f"Player {self.current_player} can only move {current_player_color} pieces!")
            return False

        if end_cell_str in self.board_status:
            target_piece = self.board_status[end_cell_str]
            if target_piece.color == piece.color:
                print(f"Cannot capture your own {target_piece}!")
                return False
            self.captured_pieces[target_piece.color].append(target_piece)
            eating = True
        else:
            eating = False

        if piece.piece_type != "knight":
            path = self._get_path(start_cell, end_cell)
            if path and not self._is_path_clear(path):
                print(f"Path is blocked for {piece}!")
                return False

        if not piece.move(start_cell, end_cell, eating=eating):
            print(f"Invalid move for {piece}!")
            return False

        pre_move_status = deepcopy(self.board_status)

        self.board_status[end_cell_str] = piece
        del self.board_status[start_cell_str]
        if self.is_in_check(self.current_player):
            if self.is_in_checkmate(self.current_player):
                winner = 2 if self.current_player == 1 else 1
                winner_color = "White" if (self.player_color == "white" and winner == 1) or \
                                          (self.player_color == "black" and winner == 2) else "Black"
                self.winner = winner
                self.game_over = True
                self.board_status = pre_move_status
                print(f"Checkmate! {winner_color} wins!")
                return "win"
            self.board_status = pre_move_status
            print("Move leaves you in check!")
            return False

        piece.moved(start_cell, end_cell)
        self.log_move(piece, end_cell)
        print(f"Player {self.current_player} plays: {move}")
        print(str(self))

        self.turn_count += 1
        next_player = 2 if self.current_player == 1 else 1

        if self.is_in_check(next_player):
            if self.is_in_checkmate(next_player):
                winner = self.current_player
                winner_color = "White" if (self.player_color == "white" and winner == 1) or \
                                          (self.player_color == "black" and winner == 2) else "Black"
                self.winner = winner
                self.game_over = True
                print(f"Checkmate! {winner_color} wins!")
                return "win"
            print(f"Check! Player {next_player} is in check.")

        self.current_player = next_player
        return True

    def _get_path(self, start: ChessCell, end: ChessCell):
        path = []
        di, dj = end.dist(start)

        step_i = 0 if di == 0 else (1 if di > 0 else -1)
        step_j = 0 if dj == 0 else (1 if dj > 0 else -1)

        steps = max(abs(di), abs(dj))

        for step in range(1, steps):
            cell_i = start.i + step * step_i
            cell_j = start.j + step * step_j

            if cell_i < 1 or cell_i > 8 or cell_j < 1 or cell_j > 8:
                continue

            cell_str = f"{ChessCell.index_to_letter[cell_i]}{cell_j}"
            path.append(cell_str)

        return path

    def _is_path_clear(self, path):
        for cell in path:
            if cell in self.board_status:
                return False
        return True

    def _validate_move_format(self, move):
        if len(move) != 5 or move[2] != '-':
            return False

        start_cell, end_cell = move.split('-')

        if (len(start_cell) != 2 or len(end_cell) != 2 or
                start_cell[0] not in 'abcdefgh' or end_cell[0] not in 'abcdefgh' or
                not start_cell[1].isdigit() or not end_cell[1].isdigit() or
                int(start_cell[1]) < 1 or int(start_cell[1]) > 8 or
                int(end_cell[1]) < 1 or int(end_cell[1]) > 8):
            return False

        return True

    def is_in_check(self, player):
        player_color = "white" if self.player_color == "white" and player == 1 else "black"
        player_color = "black" if self.player_color == "white" and player == 2 else player_color
        player_color = "white" if self.player_color == "black" and player == 2 else player_color
        player_color = "black" if self.player_color == "black" and player == 1 else player_color

        king_position = None
        for pos, piece in self.board_status.items():
            if piece.piece_type == "king" and piece.color == player_color:
                king_position = pos
                break

        if not king_position:
            return False

        opponent_color = "black" if player_color == "white" else "white"
        king_cell = ChessCell(king_position)

        for pos, piece in self.board_status.items():
            if piece.color != opponent_color:
                continue

            start_cell = ChessCell(pos)

            if piece.piece_type == "knight":
                if piece.move(start_cell, king_cell, eating=True):
                    return True
            else:
                if piece.move(start_cell, king_cell, eating=True):
                    path = self._get_path(start_cell, king_cell)
                    if self._is_path_clear(path):
                        return True

        return False

    def is_in_checkmate(self, player):
        if not self.is_in_check(player):
            return False

        player_color = "white" if self.player_color == "white" and player == 1 else "black"
        player_color = "black" if self.player_color == "white" and player == 2 else player_color
        player_color = "white" if self.player_color == "black" and player == 2 else player_color
        player_color = "black" if self.player_color == "black" and player == 1 else player_color

        for start_pos, piece in list(self.board_status.items()):
            if piece.color != player_color:
                continue

            start_cell = ChessCell(start_pos)

            for i in range(1, 9):
                for j in range(1, 9):
                    end_pos = f"{ChessCell.index_to_letter[i]}{j}"
                    if end_pos == start_pos:
                        continue

                    end_cell = ChessCell(end_pos)

                    eating = end_pos in self.board_status

                    if eating and self.board_status[end_pos].color == player_color:
                        continue

                    if piece.piece_type != "knight":
                        path = self._get_path(start_cell, end_cell)
                        if path and not self._is_path_clear(path):
                            continue

                    if not piece.move(start_cell, end_cell, eating=eating):
                        continue

                    pre_move_status = deepcopy(self.board_status)
                    captured_piece = None

                    if end_pos in self.board_status:
                        captured_piece = self.board_status[end_pos]

                    self.board_status[end_pos] = piece
                    del self.board_status[start_pos]

                    still_in_check = self.is_in_check(player)

                    self.board_status = pre_move_status

                    if not still_in_check:
                        print(f"Escape move found: {start_pos}-{end_pos}")
                        temp_board = deepcopy(self.board_status)
                        temp_board[end_pos] = temp_board[start_pos]
                        del temp_board[start_pos]

                        return False

        print("No escape moves found - checkmate!")
        return True