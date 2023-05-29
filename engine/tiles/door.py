import pygame
from engine.tiles.tile import Tile
from os.path import join

class Door(Tile):
    def __init__(self, x, y, direction="UP", is_open=False):
        self.door_up = direction == "UP"
        self.door_down = direction == "DOWN"
        self.door_left = direction == "LEFT"
        self.door_right = direction == "RIGHT"
        self.is_open = is_open
        self.res = pygame.image.load(join("resources", "textures", "door_closed.png")).convert_alpha()
        if is_open:
            self.open()

        Tile.__init__(self, x, y, 0, self.res, True)

    def collide_player(self, player, map):
        return

    def open(self):
        self.is_open = True
        self.res = pygame.image.load(join("resources", "textures", "door.png")).convert_alpha()

class TrapDoor(Tile):
    def __init__(self, x, y):
        self.res = pygame.image.load(join("resources", "textures", "trapdoor.png")).convert_alpha()

        Tile.__init__(self, x, y, 0, self.res, True)
