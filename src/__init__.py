from .gameregistry import GameRegistry
from .game.chess import ChessGame
from .game.tictactoe import TicTacToeGame

GameRegistry.register("chess", ChessGame)
GameRegistry.register("tic tac toe", TicTacToeGame)

__all__ = ["GameRegistry"]