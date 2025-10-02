import json
import itertools
import time

from .gameregistry import GameRegistry
from .players import PLAYER_REGISTRY

from datetime import datetime
from copy import deepcopy
import random


class LLMTournament:
    def __init__(self, game_name, llm_models, max_turns=50, games_per_pair=2):
        if not GameRegistry.is_valid_game(game_name):
            raise ValueError(f"Game '{game_name}' not found in registry")

        self.game_name = game_name
        self.game_class = GameRegistry.get_game(game_name)
        self.llm_models = llm_models
        self.max_turns = max_turns
        self.games_per_pair = games_per_pair
        self.results = {
            "tournament_info": {
                "game": game_name,
                "models": llm_models,
                "max_turns": max_turns,
                "games_per_pair": games_per_pair,
                "timestamp": datetime.now().isoformat()
            },
            "games": [],
            "statistics": {}
        }

    def create_ai_player(self, model_name, player_number, color):
        player_types = self.game_class.get_player_types()

        if "ai" not in player_types:
            raise ValueError(f"Game '{self.game_name}' does not support AI players")

        player_class_name = player_types["ai"]
        player_class = PLAYER_REGISTRY[player_class_name]

        player = player_class(player_number, color)
        player.model = model_name
        return player

    def play_single_game(self, model1, model2, game_id):
        colors = self.game_class.get_default_colors()
        random.shuffle(colors)
        player1_color = colors[0]
        player2_color = colors[1]

        game = self.game_class(self.max_turns, player1_color)

        player1 = self.create_ai_player(model1, 1, player1_color)
        player2 = self.create_ai_player(model2, 2, player2_color)
        player1.game = game
        player2.game = game

        players = {1: player1, 2: player2}

        game_record = {
            "game_id": game_id,
            "player1": {"model": model1, "color": player1_color},
            "player2": {"model": model2, "color": player2_color},
            "moves": [],
            "errors": {"player1": 0, "player2": 0},
            "skipped_turns": {"player1": 0, "player2": 0},
            "winner": None,
            "game_status": "in_progress",
            "final_board": None,
            "game_log": [],
            "turn_count": 0
        }

        consecutive_errors = {1: 0, 2: 0}

        print(f"Starting game {game_id}: {model1} ({player1_color}) vs {model2} ({player2_color})")
        print(str(game))

        while not game.game_over and game.turn_count < self.max_turns:
            current_player_num = game.current_player
            current_player = players[current_player_num]

            if consecutive_errors[current_player_num] >= 5:
                print(f"Player {current_player_num} has made 5 consecutive errors. Skipping turn.")
                game_record["skipped_turns"][f"player{current_player_num}"] += 1
                consecutive_errors[current_player_num] = 0
                game.current_player = 2 if current_player_num == 1 else 1
                game.turn_count += 1
                continue

            try:
                if len(game.gamelog) == 0:
                    move = current_player.get_move("")
                else:
                    move = current_player.get_move(game.formatted_gamelog)

                result = game.play_move(move)

                move_record = {
                    "player": current_player_num,
                    "model": current_player.model,
                    "move": move,
                    "valid": False,
                    "turn": game.turn_count,
                    "result": None
                }

                if result == "win":
                    move_record["valid"] = True
                    move_record["result"] = "win"
                    game_record["winner"] = current_player_num
                    game_record["game_status"] = "checkmate"
                    consecutive_errors[current_player_num] = 0
                elif result:
                    move_record["valid"] = True
                    move_record["result"] = "continue"
                    consecutive_errors[current_player_num] = 0
                else:
                    move_record["valid"] = False
                    move_record["result"] = "invalid_move"
                    game_record["errors"][f"player{current_player_num}"] += 1
                    consecutive_errors[current_player_num] += 1

                game_record["moves"].append(move_record)

            except Exception as e:
                print(f"Error getting move from player {current_player_num}: {e}")
                game_record["errors"][f"player{current_player_num}"] += 1
                consecutive_errors[current_player_num] += 1

                error_record = {
                    "player": current_player_num,
                    "model": current_player.model,
                    "move": "ERROR",
                    "valid": False,
                    "turn": game.turn_count,
                    "result": "exception",
                    "error": str(e)
                }
                game_record["moves"].append(error_record)

        if not game.game_over and game.turn_count >= self.max_turns:
            game_record["game_status"] = "max_turns_reached"

        game_record["turn_count"] = game.turn_count
        game_record["game_log"] = game.gamelog.copy()

        try:
            game_record["final_board"] = {pos: {"piece": piece.piece_type, "color": piece.color}
                                          for pos, piece in game.board_status.items()}
        except AttributeError:
            game_record["final_board"] = game.board_status.copy()

        return game_record

    def run_tournament(self):
        game_counter = 1

        for model1, model2 in itertools.combinations_with_replacement(self.llm_models, 2):
            games_to_play = self.games_per_pair if model1 != model2 else 1

            for game_num in range(games_to_play):
                game_record = self.play_single_game(model1, model2, game_counter)
                self.results["games"].append(game_record)
                game_counter += 1

                time.sleep(2)

        self.calculate_statistics()

    def calculate_statistics(self):
        stats = {}

        for model in self.llm_models:
            stats[model] = {
                "games_played": 0,
                "wins": 0,
                "losses": 0,
                "draws": 0,
                "total_moves": 0,
                "valid_moves": 0,
                "invalid_moves": 0,
                "total_errors": 0,
                "skipped_turns": 0,
                "win_rate": 0,
                "move_accuracy": 0,
                "avg_moves_per_game": 0
            }

        for game in self.results["games"]:
            model1 = game["player1"]["model"]
            model2 = game["player2"]["model"]

            stats[model1]["games_played"] += 1
            stats[model2]["games_played"] += 1

            if game["winner"] == 1:
                stats[model1]["wins"] += 1
                stats[model2]["losses"] += 1
            elif game["winner"] == 2:
                stats[model2]["wins"] += 1
                stats[model1]["losses"] += 1
            else:
                stats[model1]["draws"] += 1
                stats[model2]["draws"] += 1

            stats[model1]["total_errors"] += game["errors"]["player1"]
            stats[model2]["total_errors"] += game["errors"]["player2"]

            stats[model1]["skipped_turns"] += game["skipped_turns"]["player1"]
            stats[model2]["skipped_turns"] += game["skipped_turns"]["player2"]

            for move in game["moves"]:
                player_num = move["player"]
                model = move["model"]

                stats[model]["total_moves"] += 1

                if move["valid"]:
                    stats[model]["valid_moves"] += 1
                else:
                    stats[model]["invalid_moves"] += 1

        for model in self.llm_models:
            model_stats = stats[model]
            if model_stats["games_played"] > 0:
                model_stats["win_rate"] = model_stats["wins"] / model_stats["games_played"]
                model_stats["avg_moves_per_game"] = model_stats["total_moves"] / model_stats["games_played"]

            if model_stats["total_moves"] > 0:
                model_stats["move_accuracy"] = model_stats["valid_moves"] / model_stats["total_moves"]

        self.results["statistics"] = stats

    def save_results(self, filename=None):
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"llm_{self.game_name}_tournament_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"Tournament results saved to {filename}")
        return filename

    def print_summary(self):
        print("\n" + "=" * 60)
        print(f"TOURNAMENT SUMMARY - {self.game_name.upper()}")
        print("=" * 60)

        for model, stats in self.results["statistics"].items():
            print(f"\n{model.upper()}:")
            print(f"  Games: {stats['games_played']}")
            print(f"  W/L/D: {stats['wins']}/{stats['losses']}/{stats['draws']}")
            print(f"  Win Rate: {stats['win_rate']:.2%}")
            print(f"  Move Accuracy: {stats['move_accuracy']:.2%}")
            print(f"  Total Errors: {stats['total_errors']}")
            print(f"  Skipped Turns: {stats['skipped_turns']}")
            print(f"  Avg Moves/Game: {stats['avg_moves_per_game']:.1f}")


if __name__ == "__main__":
    llm_models = [
        "qwen3:8b",
        "mistral"
    ]

    tournament = LLMTournament(
        game_name="chess",
        llm_models=llm_models,
        max_turns=5,
        games_per_pair=2
    )

    tournament.run_tournament()
    tournament.print_summary()
    filename = tournament.save_results()

    print(f"\nDetailed results saved to: {filename}")