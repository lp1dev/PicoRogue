import pygame
from engine.tiles.tile import Tile
from os.path import join

class Flame(Tile):
    def __init__(self, x, y, damage=1, res=None, collide=True):
        self.lives = 3
        Tile.__init__(self, x, y, damage, res, collide)

    def hit(self):
        if self.lives > 1:
            self.lives -= 1
            self.res = pygame.image.load(join("resources", "textures", "fire%s.png" %self.lives)).convert_alpha()
        else:
            self.destroyed = True