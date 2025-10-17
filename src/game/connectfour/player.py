from src.players import HumanPlayer, AIPlayer


class ConnectFourHumanPlayer(HumanPlayer):
    def __init__(self, player_number, color):
        player_prompt = "Player {player_number} ({color}), enter your column (1-7): "
        super().__init__(player_number, color.capitalize(), player_prompt)

    def get_move(self, game):
        move = input(self.player_prompt.format(player_number=self.player_number, color=self.color))
        return move


class ConnectFourAIPlayer(AIPlayer):
    def __init__(self, player_number, color, model="gpt-oss:120b-cloud"):
        prompt_format = """
        You are playing Connect Four as {symbol}.

        GAME RULES:
        - The objective is to get four of your pieces in a row
        - You can win by getting 4 in a row horizontally, vertically, or diagonally
        - Pieces fall to the lowest available position in the column
        - Block your opponent from getting 4 in a row
        - Red always plays first, Yellow plays second

        The board has 7 columns (numbered 1-7) and 6 rows.

        Current game state:
        {board_display}

        Column status:
        {column_status}

        Available columns you can choose from:
        {available_list}

        STRATEGY TIPS:
        - If you can win on this move, play the winning column
        - If opponent can win on their next move, block them
        - Center column (4) is strategically valuable
        - Try to build multiple threats simultaneously
        - Be careful not to set up your opponent for a win by playing underneath their potential winning position

        Choose ONE available column from the list above.

        Respond ONLY with the move in JSON format.
        """

        response_schema = {
            "type": "object",
            "properties": {
                "move": {
                    "description": "The column number to drop your piece (must be from available columns)",
                    "type": "string",
                    "pattern": "^[1-7]$"
                },
            },
            "required": [
                "move",
            ]
        }
        super().__init__(player_number, color.capitalize(), model, prompt_format, response_schema)

    def get_move(self, game):
        print(f"AI Player {self.player_number} ({self.color}) is thinking...")

        symbol = "R" if self.color == "RED" else "Y"

        board_lines = []
        for row in range(game.rows):
            line = ""
            for col in range(game.columns):
                piece = game.board[row][col]
                if piece is None:
                    line += " ·"
                else:
                    line += f" {piece}"
            board_lines.append(line)
        board_lines.append(" 1 2 3 4 5 6 7")
        board_display = "\n".join(board_lines)

        column_status = []
        available_columns = []
        for col in range(1, 8):
            if game.board[0][col - 1] is None:
                available_columns.append(str(col))
                pieces_in_col = 0
                for row in range(game.rows):
                    if game.board[row][col - 1] is not None:
                        pieces_in_col += 1
                column_status.append(f"Column {col}: {6 - pieces_in_col} spaces left")
            else:
                column_status.append(f"Column {col}: FULL")

        column_status_str = ", ".join(column_status)
        available_list = ", ".join(available_columns)

        message = self.prompt_format.format(
            symbol=symbol,
            board_display=board_display,
            column_status=column_status_str,
            available_list=available_list
        )

        move = self._prompt_model(message=message)
        return move