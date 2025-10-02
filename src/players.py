from ollama import chat
import json


class Player:
    def __init__(self, player_number, color):
        self.player_number = player_number
        self.color = color

    def get_move(self, board_status):
        raise NotImplementedError

    def notify_move(self, move, board_status):
        pass


class HumanPlayer(Player):
    def get_move(self, board_status):
        move = input(f"Player {self.player_number} ({self.color}), enter your move (e.g., 'e2-e4'): ")
        return move


class AIPlayer(Player):
    def __init__(self, player_number, color):
        super().__init__(player_number, color)
        self.prompt_format = """
        You are playing chess as the {color} pieces. 

        These are the positions of the white and black chess pieces in algebraic notation:
        {board_status}

        Make your next move using algebraic notation (a-h for columns, 1-8 for rows)

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
        self.model = "mistral"
        self.game = None

    def get_move(self, board_status):
        print(f"AI Player {self.player_number} ({self.color}) is thinking...")

        board_visual = {"white": [], "black": []}

        for position, piece in board_status.items():
            piece_representation = f"{piece.piece_initial}{position}"

            board_visual[piece.color].append(piece_representation)

        response = chat(
            model=self.model,
            messages=[{'role': 'user',
                       'content': self.prompt_format.format(color=self.color, board_status=board_visual)}],
            format=self.response_schema,
            stream=False,
        )
        content = json.loads(response.message.content)

        print(board_visual)
        print(content)
        return content["start"] + "-" + content["end"]

class MoveslogAiplayer(Player):
    def __init__(self, player_number, color):
        super().__init__(player_number, color)
        self.prompt_format = """
        Here is the game log of a chess game in algebraic notation:
        {formatted_gamelog}

        Decide the next move using long algebraic notation

        Respond ONLY with the move in JSON format.
        """
        self.response_schema = {
            "type": "object",
            "properties": {
                "move": {
                    "description": "The next move in long algebraic notation",
                    "type": "string",
                    "pattern": "^[KNQBR]?[a-h][1-8][a-h][1-8]$"
                },
            },
            "required": [
                "move",
            ]
        }
        self.model = "mistral"
        self.game = None

    def get_move(self, board_status):
        print(f"AI Player {self.player_number} ({self.color}) is thinking...")

        if len(board_status) == 0:
            message = f"You are playing the {self.color} pieces in a chess game. Decide the first move using long algebraic notation. Respond ONLY with the move in JSON format."
        else:
            message = self.prompt_format.format(color=self.color, formatted_gamelog=board_status)

        response = chat(
            model=self.model,
            messages=[{'role': 'user',
                       'content': message}],
            format=self.response_schema,
            stream=False,
        )
        move = json.loads(response.message.content)["move"]

        print(move)
        if "x" in move or "-" in move:
            del move[-3]
        return move[-4:-2] + "-" + move[-2:]


PLAYER_REGISTRY = {
    "HumanPlayer": HumanPlayer,
    "AIPlayer": AIPlayer,
    "MoveslogAiplayer": MoveslogAiplayer
}