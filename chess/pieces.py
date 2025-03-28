from abc import ABC
from cells import ChessCell


class Piece(ABC):
    def __init__(self, color, piece_type):
        self.color = color
        self.piece_type = piece_type

    def __str__(self):
        return f"{self.color} {self.piece_type}"

    def move(self, start: ChessCell, end: ChessCell, **kwargs) -> bool:
        raise NotImplementedError


class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color, "pawn")
        self.ever_moved = False

    def move(self, start: ChessCell, end: ChessCell, **kwargs):
        distance_i, distance_j = end.dist(start)
        eating = kwargs.get("eating", False)

        if not self.ever_moved:
            if distance_i == 0 and 0 < distance_j <= 2:
                return True
            else:
                return False
        else:
            if eating:
                if distance_i == 1 and distance_j == 1:
                    return True
                else:
                    return False
            else:
                if distance_i == 0 and distance_j == 1:
                    return True
                else:
                    return False


class Rook(Piece):
    def __init__(self, color):
        super().__init__(color, "rook")

    def move(self, start: ChessCell, end: ChessCell, **kwargs):
        distance_i, distance_j = end.dist(start)

        return distance_i == 0 or distance_j == 0


class Knight(Piece):
    def __init__(self, color):
        super().__init__(color, "knight")

    def move(self, start: ChessCell, end: ChessCell, **kwargs):
        distance_i, distance_j = end.dist(start)

        return (abs(distance_i) == 2 and abs(distance_j) == 1) or \
            (abs(distance_i) == 1 and abs(distance_j) == 2)


class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color, "bishop")

    def move(self, start: ChessCell, end: ChessCell, **kwargs):
        distance_i, distance_j = end.dist(start)

        return abs(distance_i) == abs(distance_j)


class Queen(Piece):
    def __init__(self, color):
        super().__init__(color, "queen")

    def move(self, start: ChessCell, end: ChessCell, **kwargs):
        distance_i, distance_j = end.dist(start)

        return distance_i == 0 or distance_j == 0 or abs(distance_i) == abs(distance_j)


class King(Piece):
    def __init__(self, color):
        super().__init__(color, "king")
        self.ever_moved = False

    def move(self, start: ChessCell, end: ChessCell, **kwargs):
        distance_i, distance_j = end.dist(start)

        return abs(distance_i) <= 1 and abs(distance_j) <= 1

