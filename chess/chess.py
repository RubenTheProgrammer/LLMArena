from copy import deepcopy

from Players import HumanPlayer, AIPlayer, MoveslogAiplayer
from cells import ChessCell
from pieces import Pawn, Rook, Knight, Bishop, Queen, King

#TODO creare uno script che data una list di modelli (LLM) fa tutte le combinazioni di giocatori e crea un report (un file che salvo)


class ChessGame:
    def __init__(self, max_turns, player_color):
        self.max_turns = max_turns
        self.turn_count = 0
        #modify initial current_player based on player's color choice
        self.current_player = 2 if player_color == "black" else 1
        self.player_color = player_color
        self.board_status = self.initialize_pieces()
        self.board_size = 8
        self.captured_pieces = {"white": [], "black": []}
        self.winner = None  #track the winner
        self.game_over = False  #track if game is over
        self.gamelog = []


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

    def initialize_pieces(self):
        #using the actual piece classes from pieces.py
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

    @property
    def formatted_gamelog(self):
        counter = 1
        formatted_gamelog = []
        for i in range(0, len(self.gamelog), 2):
            whitemove = self.gamelog[i]
            if i + 1 < len(self.gamelog):
                blackmove = self.gamelog[i + 1]
            else:
                blackmove = ""
            formatted_gamelog.append(f"{counter}. {whitemove} {blackmove}")
            counter += 1

        formatted_gamelog = "\n".join(formatted_gamelog)
        return formatted_gamelog


    def play_move(self, move):
        # more robust move validation
        if not self._validate_move_format(move):
            print(f"Move '{move}' is not valid!")
            return False

        # parse move
        start_cell_str, end_cell_str = move.split('-')
        start_cell = ChessCell(start_cell_str)
        end_cell = ChessCell(end_cell_str)

        # check if a piece exists at the start cell
        if start_cell_str not in self.board_status:
            print(f"No piece at {start_cell_str}!")
            return False

        piece = self.board_status[start_cell_str]

        # validate piece color matches current player
        if self.player_color == "white":
            # if player is white, 1 is white, 2 is black
            current_player_color = "white" if self.current_player == 1 else "black"
        else:
            # if player is black, 1 is black, 2 is white
            current_player_color = "black" if self.current_player == 1 else "white"

        if piece.color.lower() != current_player_color:
            print(f"Player {self.current_player} can only move {current_player_color} pieces!")
            return False

        if end_cell_str in self.board_status:
            target_piece = self.board_status[end_cell_str]
            if target_piece.color == piece.color:
                print(f"Cannot capture your own {target_piece}!")
                return False
            # add the captured piece to the appropriate list
            self.captured_pieces[target_piece.color].append(target_piece)
            eating = True
        else:
            eating = False

        # knights can jump over pieces, so only check the destination
        if piece.piece_type != "knight":
            # check if the path is clear
            path = self._get_path(start_cell, end_cell)
            if path and not self._is_path_clear(path):
                print(f"Path is blocked for {piece}!")
                return False

        # validate piece movement with eating information for pawns
        if not piece.move(start_cell, end_cell, eating=eating):
            print(f"Invalid move for {piece}!")
            return False

        # move the piece if does not end in a check
        pre_move_status = deepcopy(self.board_status)

        # simulate move
        self.board_status[end_cell_str] = piece
        del self.board_status[start_cell_str]
        if self.is_in_check(self.current_player):
            # add checkmate check
            if self.is_in_checkmate(self.current_player):
                winner = 2 if self.current_player == 1 else 1
                winner_color = "White" if (self.player_color == "white" and winner == 1) or \
                                          (self.player_color == "black" and winner == 2) else "Black"
                self.winner = winner
                self.game_over = True
                self.board_status = pre_move_status
                print(f"Checkmate! {winner_color} wins!")
                return "win"  # return a special status to indicate a win
            self.board_status = pre_move_status
            print("Move leaves you in check!")
            return False

        # Move was successful, update the board
        piece.moved(start_cell, end_cell)
        self.log_move(piece, end_cell)
        print(f"Player {self.current_player} plays: {move}")
        print(str(self))

        # Increment turn and set next player
        self.turn_count += 1
        next_player = 2 if self.current_player == 1 else 1

        # Check if the move puts the opponent in checkmate
        if self.is_in_check(next_player):
            if self.is_in_checkmate(next_player):
                # The opponent is in checkmate - current player wins
                winner = self.current_player  # The player who just moved wins
                winner_color = "White" if (self.player_color == "white" and winner == 1) or \
                                          (self.player_color == "black" and winner == 2) else "Black"
                self.winner = winner
                self.game_over = True
                print(f"Checkmate! {winner_color} wins!")
                return "win"  # Return a special status to indicate a win
            print(f"Check! Player {next_player} is in check.")

        # Update current player and continue the game
        self.current_player = next_player
        return True

    def _get_path(self, start: ChessCell, end: ChessCell):
        path = []
        di, dj = end.dist(start)

        #determine direction
        step_i = 0 if di == 0 else (1 if di > 0 else -1)
        step_j = 0 if dj == 0 else (1 if dj > 0 else -1)

        #calculate number of steps
        steps = max(abs(di), abs(dj))

        #generate each cell in the path
        for step in range(1, steps):
            cell_i = start.i + step * step_i
            cell_j = start.j + step * step_j

            #verify cell is within board boundaries
            if cell_i < 1 or cell_i > 8 or cell_j < 1 or cell_j > 8:
                continue  #skip this cell if it's outside the board

            cell_str = f"{ChessCell.index_to_letter[cell_i]}{cell_j}"
            path.append(cell_str)

        return path

    def _is_path_clear(self, path):
        for cell in path:
            if cell in self.board_status:
                return False
        return True

    def _validate_move_format(self, move):
        #validate move format
        if len(move) != 5 or move[2] != '-':
            return False

        start_cell, end_cell = move.split('-')

        #validate cell format
        if (len(start_cell) != 2 or len(end_cell) != 2 or
                start_cell[0] not in 'abcdefgh' or end_cell[0] not in 'abcdefgh' or
                not start_cell[1].isdigit() or not end_cell[1].isdigit() or
                int(start_cell[1]) < 1 or int(start_cell[1]) > 8 or
                int(end_cell[1]) < 1 or int(end_cell[1]) > 8):
            return False

        return True

    def is_in_check(self, player):
        # first, find the king
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
            return False  # no king found (shouldn't happen in normal chess)

        # check if any opponent piece can capture the king
        opponent_color = "black" if player_color == "white" else "white"  # color of the opponent's pieces
        king_cell = ChessCell(king_position)  # the cell where the king is located

        for pos, piece in self.board_status.items():
            if piece.color != opponent_color:
                continue

            start_cell = ChessCell(pos)

            # knights can jump, so no need to check path for them
            if piece.piece_type == "knight":
                if piece.move(start_cell, king_cell, eating=True):
                    return True
            else:
                # for other pieces, check both the move validity and path clearance
                if piece.move(start_cell, king_cell, eating=True):
                    path = self._get_path(start_cell, king_cell)
                    if self._is_path_clear(path):
                        return True

        # only return False after checking all opponent pieces
        return False

    def is_in_checkmate(self, player):
        # If not in check, not in checkmate
        if not self.is_in_check(player):
            return False

        # Get player color
        player_color = "white" if self.player_color == "white" and player == 1 else "black"
        player_color = "black" if self.player_color == "white" and player == 2 else player_color
        player_color = "white" if self.player_color == "black" and player == 2 else player_color
        player_color = "black" if self.player_color == "black" and player == 1 else player_color

        # Try all possible moves for all pieces of the player
        for start_pos, piece in list(self.board_status.items()):
            if piece.color != player_color:
                continue

            start_cell = ChessCell(start_pos)

            # Try all possible destination cells
            for i in range(1, 9):
                for j in range(1, 9):
                    end_pos = f"{ChessCell.index_to_letter[i]}{j}"
                    if end_pos == start_pos:
                        continue

                    end_cell = ChessCell(end_pos)

                    # Check if there's a piece at the destination
                    eating = end_pos in self.board_status

                    # Can't capture own piece
                    if eating and self.board_status[end_pos].color == player_color:
                        continue

                    # For non-knights, check path clearance
                    if piece.piece_type != "knight":
                        path = self._get_path(start_cell, end_cell)
                        if path and not self._is_path_clear(path):
                            continue

                    # Check if move is valid for this piece
                    if not piece.move(start_cell, end_cell, eating=eating):
                        continue

                    # Simulate the move
                    pre_move_status = deepcopy(self.board_status)
                    captured_piece = None

                    if end_pos in self.board_status:
                        captured_piece = self.board_status[end_pos]

                    # Make the move
                    self.board_status[end_pos] = piece
                    del self.board_status[start_pos]

                    # Check if still in check after the move
                    still_in_check = self.is_in_check(player)

                    #restore the board
                    self.board_status = pre_move_status

                    #if the move gets out of check, then it's not checkmate
                    if not still_in_check:
                        print(f"Escape move found: {start_pos}-{end_pos}")
                        temp_board = deepcopy(self.board_status)
                        temp_board[end_pos] = temp_board[start_pos]
                        del temp_board[start_pos]

                        return False

        # No legal moves found that escape check - it's checkmate
        print("No escape moves found - checkmate!")
        return True


# Define games dictionary after ChessGame class
games = {"chess": ChessGame}
player_color = ["white", "black"]


class GameController:
    def __init__(self):
        self.game = None
        self.players = {}

    def ask_user(self):
        #which game?
        game = input("Which game? (chess): ").strip().lower()
        if game in games:
            turns_input = input("How many turns? ")

            #validate turns input
            if not turns_input.isnumeric():
                print("Not a valid amount of turns!")
                return False

            turns = int(turns_input)

            #check if turns are within acceptable range
            if turns > 50:
                print("Not a valid amount of turns!")
                return False

            color_choice = input("What color should Player 1 be? ").strip().lower()
            if color_choice in player_color:
                #create the game
                self.game = games[game](turns, color_choice)

                #ask about player types for both players
                player2_color = "black" if color_choice == "white" else "white"

                #validate player type inputs
                valid_player_types = ["human", "ai"]

                #get and validate player 1 type
                player1_type = ""
                while player1_type not in valid_player_types:
                    player1_type = input(
                        f"Player 1 ({color_choice.capitalize()}): Human or AI? (human/ai): ").strip().lower()
                    if player1_type not in valid_player_types:
                        print("Invalid player type! Please enter 'human' or 'ai'.")

                #get and validate player 2 type
                player2_type = ""
                while player2_type not in valid_player_types:
                    player2_type = input(
                        f"Player 2 ({player2_color.capitalize()}): Human or AI? (human/ai): ").strip().lower()
                    if player2_type not in valid_player_types:
                        print("Invalid player type! Please enter 'human' or 'ai'.")

                #create players based on choices
                ai_player_types = {
                    "ai": MoveslogAiplayer
                }
                if player1_type in ai_player_types:
                    self.players[1] = ai_player_types[player1_type](1, color_choice)
                    self.players[1].game = self.game
                else:
                    self.players[1] = HumanPlayer(1, color_choice)

                if player2_type in ai_player_types:
                    self.players[2] = ai_player_types[player2_type](2, player2_color.lower())
                    self.players[2].game = self.game
                else:
                    self.players[2] = HumanPlayer(2, player2_color.lower())

                return True
            else:
                print("Color not recognized!")
                return False
        else:
            print("Game not recognized!")
            return False

    def play(self):

        #only start the game if ask_user() was successful
        if self.game is None:
            print("Please start a valid game first.")
            return

        turn_count = 0
        print(str(self.game))

        game_over = False
        #add a check for if both players are AI to add a delay
        both_ai = all(isinstance(player, AIPlayer) for player in self.players.values())
        if both_ai:
            import time
            delay = input("Both players are AI. Enter delay between moves in seconds (default 1): ")
            try:
                delay = float(delay) if delay.strip() else 1.0
            except ValueError:
                delay = 1.0

        while not game_over and turn_count < self.game.max_turns:
            print(f"\n--- Turn {turn_count} ---")

            # get the current player
            current_player = self.players[self.game.current_player]

            # get the move from the player
            if isinstance(current_player, MoveslogAiplayer):
                move = current_player.get_move(self.game.formatted_gamelog)
            else:
                move = current_player.get_move(self.game.board_status)

            # make the move
            result = self.game.play_move(move)

            if result == "win":  # Check for win condition
                game_over = True
                print(f"Game over! Player {self.game.winner} wins!")
            elif result:  # valid move
                # notify both players of the move
                for player in self.players.values():
                    player.notify_move(move, self.game.board_status)
                turn_count += 1

                # add delay if both players are AI
                if both_ai and not game_over:
                    time.sleep(delay)

        if not game_over:
            print("Game over after", self.game.max_turns, "turns")

            # Final message for game result
        if self.game.winner:
            winner_color = self.players[self.game.winner].color.capitalize()
            print(f"Final result: {winner_color} wins!")
        else:
            print("Final result: Draw!")


# Start game
if __name__ == "__main__":
    controller = GameController()
    if controller.ask_user():
        controller.play()