from .gameregistry import GameRegistry
from .game.chess import ChessGame
from .game.tictactoe import TicTacToeGame
from .game.connectfour import ConnectFourGame

GameRegistry.register("chess", ChessGame)
GameRegistry.register("tic tac toe", TicTacToeGame)
GameRegistry.register("connect four", ConnectFourGame)

__all__ = ["GameRegistry"]