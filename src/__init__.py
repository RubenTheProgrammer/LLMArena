from .gameregistry import GameRegistry
from .game.chess import ChessGame

GameRegistry.register("chess", ChessGame)


__all__ = ["GameRegistry"]