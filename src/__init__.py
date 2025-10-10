from .gameregistry import GameRegistry
from .game.chess import ChessGame
from .game.tictactoe import TicTacToeGame

GameRegistry.register("chess", ChessGame)
GameRegistry.register("tictactoe", TicTacToeGame)

__all__ = ["GameRegistry"]