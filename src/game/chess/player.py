from src.players import HumanPlayer, AIPlayer

class ChessHumanPlayer(HumanPlayer):
    def __init__(self, player_number, color):
        player_prompt = "Player {player_number} ({color}), enter your move (e.g., 'e2-e4'): "
        super().__init__(player_number, color, player_prompt)

class ChessAIPlayer(AIPlayer):
    def __init__(self, player_number, color, model="gpt-oss:120b-cloud"):
        prompt_format = """
        Here is the game log of a chess game in algebraic notation:
        {formatted_gamelog}

        Decide the next move using long algebraic notation

        Respond ONLY with the move in JSON format.
        """
        response_schema = {
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
        super().__init__(player_number, color, model, prompt_format, response_schema)

    def get_move(self, game):
        print(f"AI Player {self.player_number} ({self.color}) is thinking...")

        if len(game.formatted_gamelog) == 0:
            message = f"You are playing the {self.color} pieces in a chess game. Decide the first move using long algebraic notation. Respond ONLY with the move in JSON format."
        else:
            message = self.prompt_format.format(color=self.color, formatted_gamelog=game.formatted_gamelog)

        move = self._prompt_model(message=message)

        if "x" in move or "-" in move:
            move = move[:-3]+move[-2:]
        return move[-4:-2] + "-" + move[-2:]