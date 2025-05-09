from abc import ABC
from cells import ChessCell


class Piece(ABC):
    def __init__(self, color: str, piece_type: str, symbol: dict[str, str]):
        self.color = color
        self.piece_type = piece_type
        self._symbol = symbol

    @property
    def symbol(self) -> str:
        return self._symbol[self.color]

    def __str__(self):
        return f"{self.color} {self.piece_type}"

    def move(self, start: ChessCell, end: ChessCell, **kwargs) -> bool:
        raise NotImplementedError

    def moved(self, start: ChessCell, end: ChessCell, **kwargs) -> bool:
        pass


class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color, "pawn", {"black": "♟", "white": "♙"})
        self.ever_moved = False

    def move(self, start: ChessCell, end: ChessCell, **kwargs):
        distance_i, distance_j = end.dist(start)
        if self.color == "black":
            distance_j *= -1  #invert for black pawns moving down
        eating = kwargs.get("eating", False)

        if eating:

            return abs(distance_i) == 1 and distance_j == 1
        else:

            if distance_i == 0:
                if not self.ever_moved:
                    return 0 < distance_j <= 2
                else:
                    return distance_j == 1
            else:
                return False

    def moved(self, start: ChessCell, end: ChessCell, **kwargs):
        self.ever_moved = True


class Rook(Piece):
    def __init__(self, color):
        super().__init__(color, "rook", {"black": "♜", "white": "♖"})

    def move(self, start: ChessCell, end: ChessCell, **kwargs):
        distance_i, distance_j = end.dist(start)

        return distance_i == 0 or distance_j == 0


class Knight(Piece):
    def __init__(self, color):
        super().__init__(color, "knight", {"black": "♞", "white": "♘"})

    def move(self, start: ChessCell, end: ChessCell, **kwargs):
        distance_i, distance_j = end.dist(start)

        return (abs(distance_i) == 2 and abs(distance_j) == 1) or \
            (abs(distance_i) == 1 and abs(distance_j) == 2)


class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color, "bishop", {"black": "♝", "white": "♗"})

    def move(self, start: ChessCell, end: ChessCell, **kwargs):
        distance_i, distance_j = end.dist(start)

        return abs(distance_i) == abs(distance_j)


class Queen(Piece):
    def __init__(self, color):
        super().__init__(color, "queen", {"black": "♛", "white": "♕"})

    def move(self, start: ChessCell, end: ChessCell, **kwargs):
        distance_i, distance_j = end.dist(start)

        return distance_i == 0 or distance_j == 0 or abs(distance_i) == abs(distance_j)


class King(Piece):
    def __init__(self, color):
        super().__init__(color, "king", {"black": "♚", "white": "♔"})
        self.ever_moved = False

    def move(self, start: ChessCell, end: ChessCell, **kwargs):
        distance_i, distance_j = end.dist(start)

        return abs(distance_i) <= 1 and abs(distance_j) <= 1

