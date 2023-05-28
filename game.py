from display import pygame_handler
from engine.player import Player
from engine.map import Map

class GameLoop:

    def __init__(self):
        self.game_data = {"floor": 1}
        self.go_on = True
        self.player = Player()
        self.output = pygame_handler.PygameHandler(64 * 15, 64 * 13, self.player)
        self.loop()
        return

    def loop(self):
        self.map = Map(self.player, self.game_data['floor'])

        while self.go_on:

            self.output.clock.tick(60)
            self.output.handle_collisions(self.map)
            self.output.handle_ennemies()
            self.output.handle_event(self.map)
            self.output.draw(self.map)
        return
