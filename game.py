from sys import argv
from display import pygame_handler
from engine.player import Player
from engine.map import Map

class GameLoop:

    def __init__(self):
        self.width = 1080
        self.height = 720
        self.FPS = 30

        if len(argv) == 3:
            self.width = int(argv[1])
            self.height = int(argv[2])
        self.game_data = {"floor": 1}
        self.go_on = True
        self.player = Player()
        self._map = Map(self.player, self.game_data['floor'])
        self.output = pygame_handler.PygameHandler(self.width, self.height, self.player, self._map, self.FPS)
        self.loop()
        return

    def loop(self):
        max_fps = 0
        while self.go_on:

            self.output.clock.tick(self.FPS)
            fps = self.output.clock.get_fps()
            if fps > max_fps:
                max_fps = fps
            # print('Max FPS: {}'.format(max_fps))
            # print('FPS: {}'.format(fps))
            self.output.handle_collisions()
            self.output.handle_ennemies()
            self.output.handle_event()
            self.output.draw()
        return
