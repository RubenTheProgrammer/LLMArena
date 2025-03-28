class ChessCell:
    _letter_to_index = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8}
    _index_to_letter = {v: k for k, v in _letter_to_index.items()}

    def __init__(self, cell: str) -> None:
        self.i = int(self._letter_to_index[cell[0]])
        self.j = int(cell[1])

    def dist(self, other):
        # Calculate the signed distance between cells
        return self.i - other.i, self.j - other.j

    def __str__(self):
        return f'{self._index_to_letter[self.i]}{self.j}'

    def move(self, distance_i: int, distance_j: int):
        finish_pos_i = self.i + distance_i
        finish_pos_j = self.j + distance_j

        # Check if the new position is within the board
        if (1 <= finish_pos_i <= 8) and (1 <= finish_pos_j <= 8):
            new_cell = ChessCell(f'{self._index_to_letter[finish_pos_i]}{finish_pos_j}')
            return new_cell
        else:
            return None

    def __eq__(self, other):
        if not isinstance(other, ChessCell):
            return False
        return self.i == other.i and self.j == other.j