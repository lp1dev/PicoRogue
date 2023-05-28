from display import pygame_handler
from engine.player import Player
from engine.map import Map

class GameLoop:

    def __init__(self):
        self.game_data = {"floor": 1}
        self.go_on = True
        self.player = Player()
        self._map = Map(self.player, self.game_data['floor'])
        self.output = pygame_handler.PygameHandler(64 * 15, 64 * 13, self.player, self._map)
        self.loop()
        return

    def loop(self):
        while self.go_on:

            self.output.clock.tick(60)
            self.output.handle_collisions()
            self.output.handle_ennemies()
            self.output.handle_event()
            self.output.draw()
        return
