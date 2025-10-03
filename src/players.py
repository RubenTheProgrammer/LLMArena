from abc import ABC, abstractmethod

from ollama import chat
import json


class Player(ABC):
    def __init__(self, player_number, color):
        self.player_number = player_number
        self.color = color

    @abstractmethod
    def get_move(self, game):
        raise NotImplementedError


class HumanPlayer(Player):
    def __init__(self, player_number, color, player_prompt):
        super().__init__(player_number, color)
        self.player_prompt = player_prompt

    def get_move(self, game):
        move = input(self.player_prompt.format(player_number=self.player_number, color=self.color))
        return move


class AIPlayer(Player, ABC):
    def __init__(self, player_number, color, model, prompt_format, response_schema):
        super().__init__(player_number, color)
        self.prompt_format = prompt_format
        self.response_schema = response_schema
        self.model = model

    def _prompt_model(self, message):
        response = chat(
            model=self.model,
            messages=[{'role': 'user',
                       'content': message}],
            format=self.response_schema,
            stream=False,
        )
        move = json.loads(response.message.content)["move"]
        return move
