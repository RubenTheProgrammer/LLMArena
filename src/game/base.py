from abc import ABC, abstractmethod


class Game(ABC):
    def __init__(self, max_turns, player_color, board_size):
        self.max_turns = max_turns
        self.turn_count = 0
        self.current_player = 2 if player_color == "black" else 1 #specific rule for chess
        self.player_color = player_color
        self.board_status = self.initialize_game()
        self.board_size = board_size
        self.winner = None
        self.game_over = False
        self.gamelog = []

    @abstractmethod
    def initialize_game(self):
        pass

    @abstractmethod
    def log_move(self, piece, end_cell):
        pass

    @abstractmethod
    def play_move(self, move):
        pass

    @property
    def formatted_gamelog(self):
        counter = 1
        formatted_gamelog = []
        for i in range(0, len(self.gamelog), 2):
            player1move = self.gamelog[i]
            if i + 1 < len(self.gamelog):
                player2move = self.gamelog[i + 1]
            else:
                player2move = ""
            formatted_gamelog.append(f"{counter}. {player1move} {player2move}")
            counter += 1

        formatted_gamelog = "\n".join(formatted_gamelog)
        return formatted_gamelog

    @classmethod
    @abstractmethod
    def get_player_types(cls):
        pass

    @classmethod
    @abstractmethod
    def get_default_colors(cls):
        pass