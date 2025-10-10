from src.players import HumanPlayer, AIPlayer


class TicTacToeHumanPlayer(HumanPlayer):
    def __init__(self, player_number, color):
        player_prompt = "Player {player_number} ({color}), enter your move (e.g., 'a1', 'b2'): "
        super().__init__(player_number, color.upper(), player_prompt)

    def get_move(self, game):
        move = input(self.player_prompt.format(player_number=self.player_number, color=self.color))
        return move


class TicTacToeAIPlayer(AIPlayer):
    def __init__(self, player_number, color, model="gpt-oss:120b-cloud"):
        prompt_format = """
        You are playing Tic Tac Toe as {symbol}.

        GAME RULES:
        - The objective is to get three of your symbols ({symbol}) in a row
        - You can win by getting 3 in a row horizontally, vertically, or diagonally
        - Block your opponent from getting 3 in a row
        - X always plays first, O plays second

        The board layout is:
        3   a3 b3 c3
        2   a2 b2 c2  
        1   a1 b1 c1

        Current game state:
        {board_display}

        Occupied positions:
        {occupied_list}

        Available positions you can choose from:
        {available_list}

        STRATEGY TIPS:
        - If you can win on this move, play the winning position
        - If opponent can win on their next move, block them
        - Center (b2) and corners (a1, a3, c1, c3) are strategically valuable

        Choose ONE available position from the list above.

        Respond ONLY with the move in JSON format.
        """

        response_schema = {
            "type": "object",
            "properties": {
                "move": {
                    "description": "The position to place your mark (must be from available positions)",
                    "type": "string",
                    "pattern": "^[abc][123]$"
                },
            },
            "required": [
                "move",
            ]
        }
        super().__init__(player_number, color.upper(), model, prompt_format, response_schema)

    def get_move(self, game):
        print(f"AI Player {self.player_number} ({self.color}) is thinking...")

        if isinstance(game, str):
            all_positions = ["a1", "a2", "a3", "b1", "b2", "b3", "c1", "c2", "c3"]
            moves = game.strip().split("\n") if game else []
            occupied = {}

            for move in moves:
                parts = move.split()
                for part in parts:
                    if len(part) >= 3 and part[0] in 'XO' and part[1:3] in all_positions:
                        occupied[part[1:3]] = part[0]

            available = [pos for pos in all_positions if pos not in occupied]

            board_lines = []
            for row in ['3', '2', '1']:
                line = f"{row}  "
                for col in ['a', 'b', 'c']:
                    pos = f"{col}{row}"
                    if pos in occupied:
                        line += f" {occupied[pos]}"
                    else:
                        line += " ·"
                board_lines.append(line)
            board_display = "\n".join(board_lines)

            occupied_list = ", ".join([f"{pos}:{symbol}" for pos, symbol in occupied.items()]) if occupied else "None"
            available_list = ", ".join(available)
        else:
            all_positions = ["a1", "a2", "a3", "b1", "b2", "b3", "c1", "c2", "c3"]
            available = [pos for pos in all_positions if pos not in game.board_status]

            board_lines = []
            for row in ['3', '2', '1']:
                line = f"{row}  "
                for col in ['a', 'b', 'c']:
                    pos = f"{col}{row}"
                    if pos in game.board_status:
                        line += f" {game.board_status[pos]}"
                    else:
                        line += " ·"
                board_lines.append(line)
            board_display = "\n".join(board_lines)

            occupied_list = ", ".join(
                [f"{pos}:{symbol}" for pos, symbol in game.board_status.items()]) if game.board_status else "None"
            available_list = ", ".join(available)

        message = self.prompt_format.format(
            symbol=self.color,
            board_display=board_display,
            occupied_list=occupied_list,
            available_list=available_list
        )

        move = self._prompt_model(message=message)
        return move