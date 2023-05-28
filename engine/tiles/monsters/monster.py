import pygame
from engine.tiles.tile import Tile
from random import randrange
from os.path import join
from engine.tiles.items import pick_item

class Monster(Tile):
    def __init__(self, x, y, damage=1, res=None, collide=True):
        self.lives = 4
        self.res = pygame.image.load(join("resources", "textures", "eye.png")).convert_alpha() if res is None else res
        Tile.__init__(self, x, y, damage, self.res, collide)

    def hit(self, damage):
        self.lives -= damage
        if self.lives < 1:
            self.destroyed = True

    def play(self):
        return

    def after_destroyed(self, pygame_handler):
        if randrange(0, 10) == 1:
            pygame_handler.tiles.append(pick_item(self.x, self.y))
        return