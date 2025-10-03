from .gameregistry import GameRegistry


class GameController:
    def __init__(self):
        self.game = None
        self.players = {}

    def ask_user(self):
        available_games = GameRegistry.get_all_games()
        game_input = input(f"Which game? ({', '.join(available_games)}): ").strip().lower()

        if not GameRegistry.is_valid_game(game_input):
            print("Game not recognized!")
            return False

        turns_input = input("How many turns? ")

        if not turns_input.isnumeric():
            print("Not a valid amount of turns!")
            return False

        turns = int(turns_input)

        if turns > 50:
            print("Not a valid amount of turns!")
            return False

        game_class = GameRegistry.get_game(game_input)
        valid_colors = game_class.get_default_colors()

        color_choice = input(f"What color should Player 1 be? ({'/'.join(valid_colors)}): ").strip().lower()
        if color_choice not in valid_colors:
            print("Color not recognized!")
            return False

        self.game = game_class(turns, color_choice)

        player2_color = valid_colors[1] if color_choice == valid_colors[0] else valid_colors[0]

        valid_player_types = list(game_class.get_player_types().keys())

        player1_type = ""
        while player1_type not in valid_player_types:
            player1_type = input(
                f"Player 1 ({color_choice.capitalize()}): Type? ({'/'.join(valid_player_types)}): ").strip().lower()
            if player1_type not in valid_player_types:
                print(f"Invalid player type! Please enter one of: {', '.join(valid_player_types)}.")

        player2_type = ""
        while player2_type not in valid_player_types:
            player2_type = input(
                f"Player 2 ({player2_color.capitalize()}): Type? ({'/'.join(valid_player_types)}): ").strip().lower()
            if player2_type not in valid_player_types:
                print(f"Invalid player type! Please enter one of: {', '.join(valid_player_types)}.")

        player_types = game_class.get_player_types()

        if player1_type in player_types:
            self.players[1] = player_types[player1_type](1, color_choice)

        if player2_type in player_types:
            self.players[2] = player_types[player2_type](2, player2_color.lower())

        return True

    def play(self):
        if self.game is None:
            print("Please start a valid game first.")
            return

        turn_count = 0
        print(str(self.game))

        game_over = False

        from .players import AIPlayer
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

            current_player = self.players[self.game.current_player]

            move = current_player.get_move(self.game)

            result = self.game.play_move(move)

            if result == "win":
                game_over = True
                print(f"Game over! Player {self.game.winner} wins!")
            elif result:
                turn_count += 1

                if both_ai and not game_over:
                    time.sleep(delay)

        if not game_over:
            print("Game over after", self.game.max_turns, "turns")

        if self.game.winner:
            winner_color = self.players[self.game.winner].color.capitalize()
            print(f"Final result: {winner_color} wins!")
        else:
            print("Final result: Draw!")