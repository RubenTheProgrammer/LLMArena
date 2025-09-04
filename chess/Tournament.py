import json
import itertools
from datetime import datetime
from copy import deepcopy
import time

from Players import MoveslogAiplayer
from chess import ChessGame


class LLMChessTournament:
    def __init__(self, llm_models, max_turns=50, games_per_matchup=2):
        self.llm_models = llm_models
        self.max_turns = max_turns
        self.games_per_matchup = games_per_matchup
        self.tournament_results = {
            "tournament_info": {
                "models": llm_models,
                "max_turns": max_turns,
                "games_per_matchup": games_per_matchup,
                "timestamp": datetime.now().isoformat()
            },
            "matchups": [],
            "model_stats": {},
            "leaderboard": []
        }

        for model in llm_models:
            self.tournament_results["model_stats"][model] = {
                "total_games": 0,
                "wins": 0,
                "losses": 0,
                "draws": 0,
                "win_rate": 0.0,
                "avg_moves_per_game": 0.0,
                "total_moves": 0,
                "games_as_white": 0,
                "games_as_black": 0,
                "wins_as_white": 0,
                "wins_as_black": 0
            }

    def create_ai_player(self, model_name, player_number, color):
        player = MoveslogAiplayer(player_number, color)
        player.model = model_name
        return player

    def play_game(self, model1, model2, model1_color):
        model2_color = "black" if model1_color == "white" else "white"

        game = ChessGame(self.max_turns, model1_color)

        player1 = self.create_ai_player(model1, 1, model1_color)
        player2 = self.create_ai_player(model2, 2, model2_color)

        player1.game = game
        player2.game = game

        players = {1: player1, 2: player2}

        game_log = {
            "model1": model1,
            "model2": model2,
            "model1_color": model1_color,
            "model2_color": model2_color,
            "moves": [],
            "winner": None,
            "winner_model": None,
            "game_length": 0,
            "result": "draw",
            "final_position": None,
            "captured_pieces": {"white": [], "black": []},
            "errors": []
        }

        turn_count = 0
        game_over = False

        while not game_over and turn_count < game.max_turns:
            current_player = players[game.current_player]
            current_model = model1 if current_player.player_number == 1 else model2

            try:
                if isinstance(current_player, MoveslogAiplayer):
                    move = current_player.get_move(game.formatted_gamelog)
                else:
                    move = current_player.get_move(game.board_status)

                game_log["moves"].append({
                    "turn": turn_count + 1,
                    "player": current_player.player_number,
                    "model": current_model,
                    "color": current_player.color,
                    "move": move,
                    "timestamp": datetime.now().isoformat()
                })

                result = game.play_move(move)

                if result == "win":
                    game_over = True
                    game_log["winner"] = game.winner
                    game_log["winner_model"] = model1 if game.winner == 1 else model2
                    game_log["result"] = "win"
                elif result:
                    for player in players.values():
                        player.notify_move(move, game.board_status)
                    turn_count += 1
                else:
                    game_log["errors"].append({
                        "turn": turn_count + 1,
                        "player": current_player.player_number,
                        "model": current_model,
                        "invalid_move": move,
                        "timestamp": datetime.now().isoformat()
                    })

            except Exception as e:
                game_log["errors"].append({
                    "turn": turn_count + 1,
                    "player": current_player.player_number,
                    "model": current_model,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                break

        game_log["game_length"] = turn_count
        game_log["final_position"] = {pos: f"{piece.color}_{piece.piece_type}"
                                      for pos, piece in game.board_status.items()}
        game_log["captured_pieces"] = game.captured_pieces

        return game_log

    def run_tournament(self):
        print(f"Starting LLM Chess Tournament with models: {self.llm_models}")
        print(f"Games per matchup: {self.games_per_matchup}")

        total_games = len(list(itertools.combinations(self.llm_models, 2))) * self.games_per_matchup * 2
        current_game = 0

        for model1, model2 in itertools.combinations(self.llm_models, 2):
            matchup_results = {
                "model1": model1,
                "model2": model2,
                "games": [],
                "summary": {
                    f"{model1}_wins": 0,
                    f"{model2}_wins": 0,
                    "draws": 0,
                    f"{model1}_wins_as_white": 0,
                    f"{model1}_wins_as_black": 0,
                    f"{model2}_wins_as_white": 0,
                    f"{model2}_wins_as_black": 0
                }
            }

            for game_num in range(self.games_per_matchup):
                for color_setup in [("white", "black"), ("black", "white")]:
                    current_game += 1
                    model1_color, model2_color = color_setup

                    print(f"Game {current_game}/{total_games}: {model1} ({model1_color}) vs {model2} ({model2_color})")

                    game_result = self.play_game(model1, model2, model1_color)
                    matchup_results["games"].append(game_result)

                    self.update_model_stats(model1, model1_color, game_result)
                    self.update_model_stats(model2, model2_color, game_result)

                    if game_result["result"] == "win":
                        winner_model = game_result["winner_model"]
                        if winner_model == model1:
                            matchup_results["summary"][f"{model1}_wins"] += 1
                            if model1_color == "white":
                                matchup_results["summary"][f"{model1}_wins_as_white"] += 1
                            else:
                                matchup_results["summary"][f"{model1}_wins_as_black"] += 1
                        else:
                            matchup_results["summary"][f"{model2}_wins"] += 1
                            if model2_color == "white":
                                matchup_results["summary"][f"{model2}_wins_as_white"] += 1
                            else:
                                matchup_results["summary"][f"{model2}_wins_as_black"] += 1
                    else:
                        matchup_results["summary"]["draws"] += 1

                    time.sleep(1)

            self.tournament_results["matchups"].append(matchup_results)

        self.calculate_final_stats()
        self.create_leaderboard()

        return self.tournament_results

    def update_model_stats(self, model, color, game_result):
        stats = self.tournament_results["model_stats"][model]
        stats["total_games"] += 1
        stats["total_moves"] += game_result["game_length"]

        if color == "white":
            stats["games_as_white"] += 1
        else:
            stats["games_as_black"] += 1

        if game_result["result"] == "win" and game_result["winner_model"] == model:
            stats["wins"] += 1
            if color == "white":
                stats["wins_as_white"] += 1
            else:
                stats["wins_as_black"] += 1
        elif game_result["result"] == "win":
            stats["losses"] += 1
        else:
            stats["draws"] += 1

    def calculate_final_stats(self):
        for model, stats in self.tournament_results["model_stats"].items():
            if stats["total_games"] > 0:
                stats["win_rate"] = stats["wins"] / stats["total_games"]
                stats["avg_moves_per_game"] = stats["total_moves"] / stats["total_games"]

    def create_leaderboard(self):
        leaderboard = []
        for model, stats in self.tournament_results["model_stats"].items():
            leaderboard.append({
                "model": model,
                "win_rate": stats["win_rate"],
                "wins": stats["wins"],
                "losses": stats["losses"],
                "draws": stats["draws"],
                "total_games": stats["total_games"],
                "avg_moves_per_game": stats["avg_moves_per_game"]
            })

        leaderboard.sort(key=lambda x: x["win_rate"], reverse=True)
        self.tournament_results["leaderboard"] = leaderboard

    def save_results(self, filename=None):
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"llm_chess_tournament_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(self.tournament_results, f, indent=2)

        print(f"Tournament results saved to {filename}")
        return filename

    def print_summary(self):
        print("\n" + "=" * 60)
        print("TOURNAMENT SUMMARY")
        print("=" * 60)

        print(f"\nModels: {', '.join(self.llm_models)}")
        print(
            f"Total Games: {sum(stats['total_games'] for stats in self.tournament_results['model_stats'].values()) // 2}")

        print("\nLEADERBOARD:")
        print("-" * 80)
        print(f"{'Rank':<5} {'Model':<20} {'Win Rate':<10} {'W':<4} {'L':<4} {'D':<4} {'Avg Moves':<10}")
        print("-" * 80)

        for i, entry in enumerate(self.tournament_results["leaderboard"], 1):
            print(
                f"{i:<5} {entry['model']:<20} {entry['win_rate']:.3f}     {entry['wins']:<4} {entry['losses']:<4} {entry['draws']:<4} {entry['avg_moves_per_game']:.1f}")


if __name__ == "__main__":
    llm_models = [
        "llama3.2",
        "deepseek-r1:7b",
        "qwen2.5",
        "mistral"
    ]

    tournament = LLMChessTournament(
        llm_models=llm_models,
        max_turns=50,
        games_per_matchup=1
    )

    results = tournament.run_tournament()
    filename = tournament.save_results()
    tournament.print_summary()

    print(f"\nDetailed results saved to: {filename}")