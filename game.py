from engine.map import Map
from time import sleep

class GameLoop:

    def __init__(self):
        self.game_data = {"floor":1}
        self.go_on = True
        self.loop()
        return

    def loop(self):
        while self.go_on:
            m = Map(self.game_data['floor'])
            sleep(1)
            return # for debugging purposes
            pass
        return
