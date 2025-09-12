from .players import MoveslogAiplayer, HumanPlayer, AIPlayer
from .game.chess import ChessGame

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
