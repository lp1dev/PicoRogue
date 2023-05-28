from display import pygame_handler
from engine.map import Map
from time import sleep

class GameLoop:

    def __init__(self):
        self.game_data = {"floor":1}
        self.go_on = True
        self.output = pygame_handler.PygameHandler(64 * 15, 64 * 13)

        self.loop()
        return

    def loop(self):
        self.map = Map(self.game_data['floor'])

        self.output.display_tiles(self.map)
        self.output.display_map(self.map)
        self.output.display_player()
        self.output.draw()
        while self.go_on:
            self.output.clock.tick(60)

            self.output.handle_event(self.map)
            
            self.output.display_tiles(self.map)
            self.output.display_map(self.map)
            self.output.display_player()
            self.output.display_bullets()
            self.output.draw()
        return
