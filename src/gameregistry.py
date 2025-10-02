class GameRegistry:
    _games = {}

    @classmethod
    def register(cls, name, game_class):
        cls._games[name.lower()] = game_class

    @classmethod
    def get_game(cls, name):
        return cls._games.get(name.lower())

    @classmethod
    def get_all_games(cls):
        return list(cls._games.keys())

    @classmethod
    def is_valid_game(cls, name):
        return name.lower() in cls._games