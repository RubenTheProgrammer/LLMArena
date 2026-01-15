from src.gamecontroller import GameController

if __name__ == "__main__":
    controller = GameController()
    if controller.ask_user():
        controller.play()