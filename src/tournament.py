import json
import itertools
import time
import os

from .gameregistry import GameRegistry

from datetime import datetime
import random


class LLMTournament:
    def __init__(self, game_name, llm_models, max_turns=50, games_per_pair=2, results_file="tournament_results.json"):
        if not GameRegistry.is_valid_game(game_name):
            raise ValueError(f"Game '{game_name}' not found in registry")

        self.game_name = game_name
        self.game_class = GameRegistry.get_game(game_name)
        self.llm_models = llm_models
        self.max_turns = max_turns
        self.games_per_pair = games_per_pair
        self.results_file = results_file
        self.results = self._load_or_create_results()

    def _load_or_create_results(self):
        # Load or create results
        if os.path.exists(self.results_file):
            with open(self.results_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {
            "last_updated": None,
            "games_played": 0,
            "models": {}
        }

    def _ensure_model_exists(self, model):
        # Initialize model stats if not present
        if model not in self.results["models"]:
            self.results["models"][model] = {
                "games": 0,
                "wins": 0,
                "losses": 0,
                "draws": 0,
                "valid_moves": 0,
                "errors": 0,
                "matches": []
            }

    def create_ai_player(self, model_name, player_number, color):
        player_types = self.game_class.get_player_types()
        if "ai" not in player_types:
            raise ValueError(f"Game '{self.game_name}' does not support AI players")
        return player_types["ai"](player_number, color, model_name)

    def play_single_game(self, model1, model2, game_id):
        colors = self.game_class.get_default_colors()
        random.shuffle(colors)

        game = self.game_class(self.max_turns, colors[0])
        player1 = self.create_ai_player(model1, 1, colors[0])
        player2 = self.create_ai_player(model2, 2, colors[1])
        players = {1: player1, 2: player2}

        stats = {
            model1: {"valid": 0, "errors": 0},
            model2: {"valid": 0, "errors": 0}
        }
        consecutive_errors = {1: 0, 2: 0}

        print(f"Game {game_id}: {model1} vs {model2}")

        while not game.game_over and game.turn_count < self.max_turns:
            current_num = game.current_player
            current_player = players[current_num]
            model = current_player.model

            if consecutive_errors[current_num] >= 5:
                consecutive_errors[current_num] = 0
                game.current_player = 2 if current_num == 1 else 1
                game.turn_count += 1
                continue

            try:
                game_log = "" if len(game.gamelog) == 0 else game.formatted_gamelog
                move = current_player.get_move(game_log)
                result = game.play_move(move)

                if result == "win":
                    stats[model]["valid"] += 1
                    consecutive_errors[current_num] = 0
                elif result:
                    stats[model]["valid"] += 1
                    consecutive_errors[current_num] = 0
                else:
                    stats[model]["errors"] += 1
                    consecutive_errors[current_num] += 1

            except Exception as e:
                print(f"Error from player {current_num}: {e}")
                stats[model]["errors"] += 1
                consecutive_errors[current_num] += 1

        # Determine winner
        winner = None
        if game.game_over:
            for num, player in players.items():
                if hasattr(game, 'winner') and game.winner == num:
                    winner = player.model
                    break

        return {
            "model1": model1,
            "model2": model2,
            "winner": winner,
            "stats": stats
        }

    def run_tournament(self):
        game_counter = 1

        # Each pair plays 1 time
        for model1, model2 in itertools.combinations(self.llm_models, 2):
            for _ in range(self.games_per_pair):
                result = self.play_single_game(model1, model2, game_counter)
                self._update_stats(result)
                game_counter += 1
                time.sleep(2)

        self.save_results()

    def _update_stats(self, game_result):
        # Update model stats from results
        model1 = game_result["model1"]
        model2 = game_result["model2"]
        winner = game_result["winner"]
        stats = game_result["stats"]

        self._ensure_model_exists(model1)
        self._ensure_model_exists(model2)

        self.results["models"][model1]["games"] += 1
        self.results["models"][model2]["games"] += 1
        self.results["games_played"] += 1

        if winner is None:
            self.results["models"][model1]["draws"] += 1
            self.results["models"][model2]["draws"] += 1
            result1 = "draw"
            result2 = "draw"
        elif winner == model1:
            self.results["models"][model1]["wins"] += 1
            self.results["models"][model2]["losses"] += 1
            result1 = "win"
            result2 = "loss"
        else:
            self.results["models"][model2]["wins"] += 1
            self.results["models"][model1]["losses"] += 1
            result1 = "loss"
            result2 = "win"

        self.results["models"][model1]["valid_moves"] += stats[model1]["valid"]
        self.results["models"][model1]["errors"] += stats[model1]["errors"]
        self.results["models"][model2]["valid_moves"] += stats[model2]["valid"]
        self.results["models"][model2]["errors"] += stats[model2]["errors"]

        self.results["models"][model1]["matches"].append({
            "opponent": model2,
            "result": result1,
            "valid_moves": stats[model1]["valid"],
            "errors": stats[model1]["errors"]
        })

        self.results["models"][model2]["matches"].append({
            "opponent": model1,
            "result": result2,
            "valid_moves": stats[model2]["valid"],
            "errors": stats[model2]["errors"]
        })

    def save_results(self, filename=None):
        # Save results to file
        if filename:
            self.results_file = filename

        self.results["last_updated"] = datetime.now().isoformat()

        with open(self.results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print("\n")
        return self.results_file

    def print_summary(self):
        print(
            f"{'MODEL':<25} {'GAMES':>6} {'WINS':>6} {'LOSSES':>6} {'DRAWS':>6} {'VALID':>8} {'ERRORS':>8} {'WIN%':>8}")
        print("=" * 80)

        for model, stats in sorted(self.results["models"].items()):
            win_rate = (stats["wins"] / stats["games"] * 100) if stats["games"] > 0 else 0
            print(f"{model:<25} {stats['games']:>6} {stats['wins']:>6} {stats['losses']:>6} "
                  f"{stats['draws']:>6} {stats['valid_moves']:>8} {stats['errors']:>8} {win_rate:>7.1f}%")

        print(f"\nTotal games played: {self.results['games_played']}")
        print(f"Last updated: {self.results['last_updated']}")


if __name__ == "__main__":
    llm_models = [
        "qwen3:8b",
        "mistral",
        "llama3.2",
        "deepseek-r1:7b",
        "gpt-oss:120b-cloud",
        "deepseek-v3.1:671b-cloud"
    ]

    tournament = LLMTournament(
        game_name="chess",
        llm_models=llm_models,
        max_turns=5,
        games_per_pair=2,
        results_file="tournament_results.json"
    )

    tournament.run_tournament()
    tournament.print_summary()