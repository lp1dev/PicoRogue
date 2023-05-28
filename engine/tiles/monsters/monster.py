import pygame
from engine.tiles.tile import Tile
from os.path import join

class Monster(Tile):
    def __init__(self, x, y, damage=1, res=None, collide=True):
        self.lives = 4
        self.res = pygame.image.load(join("resources", "textures", "eye.png")).convert_alpha() if res is None else res
        Tile.__init__(self, x, y, damage, self.res, collide)

    def hit(self):
        if self.lives > 1:
            self.lives -= 1
        else:
            self.destroyed = True

    def play(self):
        return